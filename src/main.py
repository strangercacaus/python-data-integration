import os
import time
import logging
import datetime
from dotenv import load_dotenv
import sys
from pathlib import Path

from sqlalchemy import create_engine

sys.path.append(str(Path(__file__).parent.parent.parent))


from bdt_data_integration.src.streams.notion_stream import NotionStream
from bdt_data_integration.src.utils.utils import Utils
from bdt_data_integration.src.utils.notifier import WebhookNotifier
from metadata.configuration_helper import ConfigurationHelper
from bdt_data_integration.src.utils.dbt_runner import DBTRunner


def main():
    # Create command line argument parser using the utility method
    parser = Utils.get_parser("Run the Notion data integration pipeline")
    args = parser.parse_args()

    # Configura os diferentes níveis de log para o script
    logging.basicConfig(
        level=logging.INFO,  # Set the minimum logging level (INFO instead of DEBUG to reduce noise)
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],  # Send log output to the console (screen)
    )

    notion_logger = logging.getLogger("notion_logger")
    notion_logger.setLevel(logging.DEBUG)

    postgres_logger = logging.getLogger("postgres_loader")
    postgres_logger.setLevel(logging.DEBUG)

    dbt_logger = logging.getLogger("dbt_runner")
    dbt_logger.setLevel(logging.DEBUG)

    logging.getLogger("bdt_data_integration.src.stream.notion_stream").setLevel(
        logging.DEBUG
    )

    logging.getLogger("bdt_data_integration.src.extractor.notion_extractor").setLevel(
        logging.DEBUG
    )

    logging.getLogger("bdt_data_integration.src.loader.postgres_loader").setLevel(
        logging.DEBUG
    )

    logging.getLogger("__main__").setLevel(logging.DEBUG)

    logging.getLogger("bdt_data_integration").setLevel(logging.DEBUG)

    logging.getLogger().setLevel(logging.DEBUG)

    # Carrega as variáveis de ambiente
    load_dotenv()
    origin = "notion"
    host = os.environ["DESTINATION_HOST"]
    user = os.environ["DESTINATION_ROOT_USER"]
    password = os.environ["DESTINATION_ROOT_PASSWORD"]
    db_name = os.environ["DESTINATION_DB_NAME"]
    notifier_url = os.environ["DEEPNOTE_BENDITO_BI_WEBHOOK"]

    start_time = time.time()
    notifier = WebhookNotifier(
        url=notifier_url, pipeline="notion_pipeline", silent=args.silent.lower()
    )

    # Cria uma conexão com o banco de dados de metadados e carrega as informações das tabelas que serão processadas
    url = f"postgresql+psycopg2://{user}:{password}@{host}:5432/bendito_intelligence_metadata"
    config_handler = ConfigurationHelper(url, origin)
    tables = config_handler.get_table_configuration()

    if args.table == "all":
        active_tables = [table for table in tables if table.active]
    elif args.table in [table.source_name for table in tables]:
        active_tables = [table for table in tables if table.source_name == args.table]
    else:
        raise ValueError("Nome da base de dados inválido ou não configurado")
    
    if args.full_extract.lower() == "true":
        list(map(lambda table: setattr(table, 'days_interval', 0), active_tables))

    logger = logging.getLogger("replicate_database")

    @notifier.error_handler
    
    def replicate_table(table):
        
        if args.extract.lower() == "false":
            return 1
        stream = NotionStream(table)
        stream.set_extractor()
        records = stream.extract_stream()
        stream.set_table_definition()
        stream.set_loader(
            engine=create_engine(
                f"postgresql://{user}:{password}@{host}/{db_name}?sslmode=require"
            )
        )
        try:
            stream.load_stream(
                records,
                chunksize=args.chunk_size,
            )
            return 1
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return 0

    total = len(active_tables)
    success = 0

    if args.extract.lower() == "true":

        for table in active_tables:
            config_handler.update_table_configuration(
                table.id,
                table.source_name,
                last_sync_attempt_at=datetime.datetime.now(),
            )
            check = replicate_table(table) or 0
            success += check

            if check == 1:
                config_handler.update_table_configuration(
                    table.id,
                    table.source_name,
                    last_successful_sync_at=datetime.datetime.now(),
                )

    if args.transform.lower() == "true":

        logger = logging.getLogger("dbt_runner")
        logger.info("Executando transformações dbt para os modelos do Notion")

        # Use the utility function to get the dbt project directory
        dbt_project_dir = Utils.get_dbt_project_dir()
        dbt_profiles_dir = dbt_project_dir

        # Verificar se o diretório existe
        if not dbt_project_dir.exists():
            dbt_logger.error(
                f"Diretório do projeto dbt não encontrado: {dbt_project_dir}"
            )
        else:
            dbt_logger.info(f"Usando diretório de projeto dbt: {dbt_project_dir}")

            # Verificar se existem modelos SQL na pasta notion
            notion_models_dir = dbt_project_dir / "models" / "notion"
            if not notion_models_dir.exists():
                dbt_logger.error(
                    f"Diretório de modelos notion não encontrado: {notion_models_dir}"
                )
            else:
                sql_files = list(notion_models_dir.glob("*.sql"))
                dbt_logger.info(
                    f"Encontrados {len(sql_files)} arquivos SQL no diretório {notion_models_dir}"
                )

        # Define o schema de destino para as transformações
    dbt_logger.info(f"Usando schema de destino para transformações: {origin}")

    dbt_runner = DBTRunner(
        project_dir=str(dbt_project_dir), profiles_dir=str(dbt_profiles_dir)
    )

    if args.update_dbt_config.lower() == "true":
            logger.info("Atualizando configurações dos modelos DBT...")
            dbt_runner.update_model_configs(tables, origin)

    dbt_runner.run(models=origin, target_schema=origin)

    elapsed_time_formatted = Utils.format_elapsed_time(time.time() - start_time)

    notifier.pipeline_end(
        text=f"Execução de pipeline encerrada: notion_pipeline.\nTotal de tabelas programadas para replicação: {total}, tabelas replicadas com sucesso: {success}, tempo de execução: {elapsed_time_formatted}"
    )


if __name__ == "__main__":
    main()
