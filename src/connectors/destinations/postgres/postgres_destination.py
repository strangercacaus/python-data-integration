import csv
import logging
import psycopg2
from typing import Literal

import pandas as pd
from jinja2 import Template
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import (
    SQLAlchemyError,
    ProgrammingError,
    ObjectNotExecutableError,
)

from utils import Utils
from src.destinations.base_destination import BaseLoader
from metadata.data_table import DataTable

# Create a named logger for this module
logger = logging.getLogger("postgres_loader")


class PostgresLoader(BaseLoader):
    """
    Classe para carregar dados em um banco de dados PostgreSQL.

    Esta classe fornece métodos para criar tabelas, gerenciar esquemas e carregar dados de DataFrames no PostgreSQL.
    Também suporta a criação de gatilhos e restrições para manter a integridade dos dados.

    Atributos:
        engine (Engine): O engine do SQLAlchemy para conectar ao banco de dados PostgreSQL.
        schema_file_path (str): Caminho para o arquivo de esquema de tabela.
        schema_file_type (Literal["template", "info_schema", "schema"]): Tipo de arquivo de esquema.
    """

    def __init__(
        self,
        engine: Engine = None,
        table: DataTable = None
    ):
        """
        Inicializa o PostgresLoader com os parâmetros de conexão do banco de dados.

        Args:
            engine (Engine): O engine do SQLAlchemy para conectar ao banco de dados PostgreSQL.
            schema_file_path (str): Caminho para o arquivo de esquema de tabela.
            schema_file_type (Literal["template", "info_schema", "schema"]): Tipo de arquivo de esquema.
        """
        self.engine = engine
        self.table = table

    def close_connections(self):
        """
        Fecha as conexões ativas com o banco de dados.

        Este método termina todas as conexões ativas para o banco de dados especificado.
        """
        with self.engine.connect() as connection:
            db_name = self.engine.url.database
            terminate_query = text(
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity JOIN pg_roles ON pg_stat_activity.usename = pg_roles.rolname WHERE pid <> pg_backend_pid() AND datname = '{db_name}' AND NOT pg_roles.rolsuper;"
            )
            connection.execute(terminate_query)

    def create_schema(self):
        """
        Cria um novo schema no banco de dados.

        Este método verifica se o schema já existe e, caso não exista, cria um novo schema
        com o nome especificado.

        Args:
            target_schema (str): O nome do schema a ser criado.
        """
        with self.engine.begin() as connection:
            create_schema_query = text(f"CREATE SCHEMA {self.table.origin}")
            logger.debug(f"Executando query: {create_schema_query}")
            connection.execute(create_schema_query)
            logger.info(f"Schema {self.table.origin} criado com sucesso.")

    def create_table(self):
        """
        Cria a tabela de destino com base no esquema SQL carregado.

        Este método executa o comando SQL para criar a tabela de destino e lida com erros
        caso a tabela já exista.

        Args:
            sql_command (str): O comando SQL para criar a tabela.
        """
        if Utils.validate_sql(self.table.schemaless_ddl) == False:
            raise ValueError(f"SQL Inválido em {__name__}: {self.table.schemaless_ddl}")

        with self.engine.begin() as connection:
            try:
                connection.execute(text(self.table.schemaless_ddl))
            except SQLAlchemyError as e:
                if isinstance(e, ObjectNotExecutableError):
                    logger.error(f"O comando SQL não é executável: {self.table.schemaless_ddl}")
                elif isinstance(e.orig, psycopg2.errors.DuplicateTable):
                    logger.error(f"{__name__}: A tabela já existe.")
                else:
                    logger.error(f"Um erro ocorreu: {e}")
                raise e

    def truncate_table(self):
        """
        Trunca a tabela de destino, removendo todos os registros.

        Este método remove todos os registros da tabela especificada, mantendo a estrutura da tabela.

        Args:
            target_table (str): O nome da tabela de destino.
            target_schema (str): O esquema de destino onde a tabela está localizada.
        """
        with self.engine.begin() as connection:
            truncate_query = text(f"TRUNCATE TABLE {self.table.origin}.{self.table.raw_model_name}")
            connection.execute(truncate_query)

    def drop_table(self):
        """
        Deleta a tabela de destino.

        Args:
            target_table (str): O nome da tabela de destino.
            target_schema (str): O esquema de destino onde a tabela está localizada.
        """
        with self.engine.begin() as connection:
            drop_query = text(f"DROP TABLE {self.table.origin}.{self.table.raw_model_name}")
            connection.execute(drop_query)

    def create_updated_at_trigger(self):
        """
        Cria um gatilho para atualizar a coluna de data de modificação.

        Este método cria um gatilho que atualiza a coluna de data de modificação
        sempre que uma linha na tabela é atualizada.

        Args:
            target_table (str): O nome da tabela de destino.
            target_schema (str): O esquema de destino onde a tabela está localizada.
        """
        with self.engine.begin() as connection:
            try:
                create_query = text(
                    f"CREATE TRIGGER set_updated_at_{self.table.raw_model_name} BEFORE UPDATE ON {self.table.origin}.{self.table.raw_model_name} FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()"
                )
                connection.execute(create_query)
            except ProgrammingError as e:
                if isinstance(e.orig, psycopg2.errors.DuplicateObject):
                    logger.warning(
                        f"O trigger set_updated_at_{self.table.raw_model_name} já existe, pulando a criação."
                    )
                else:
                    raise e
            except Exception as e:
                raise e

    def create_update_updated_at_function(self):
        """
        Cria uma função para atualizar a coluna de data de modificação.

        Este método cria ou substitui uma função que define a coluna de data de modificação
        para o timestamp atual.
        """
        with self.engine.begin() as connection:
            create_query = text(
                "CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$ BEGIN NEW.__updated_at = CURRENT_TIMESTAMP; RETURN NEW; END; $$ LANGUAGE plpgsql"
            )
            connection.execute(create_query)

    def create_constraint(
        self,
        column: str,
        kind=("primary_key", "unique_key"),
    ):
        """
        Cria uma restrição de chave primária ou única na tabela de destino.

        Este método adiciona uma restrição de chave primária ou única à coluna especificada
        na tabela de destino.

        Args:
            target_table (str): O nome da tabela de destino.
            target_schema (str): O esquema de destino onde a tabela está localizada.
            column (str): O nome da coluna para a qual a restrição será aplicada.
            kind (list, optional): O tipo de restrição a ser criada ('primary_key' ou 'unique_key').
        """
        with self.engine.begin() as connection:
            if kind == "primary_key":
                create_query = text(
                    f"""ALTER TABLE {self.table.origin}.{self.table.raw_model_name} ADD CONSTRAINT {self.table.raw_model_name}_pk PRIMARY KEY ("{column}")"""
                )
            elif kind == "unique_key":
                create_query = text(
                    f"""ALTER TABLE {self.table.origin}.{self.table.raw_model_name} ADD CONSTRAINT {self.table.raw_model_name}__unique UNIQUE ("{column}")"""
                )
            connection.execute(create_query)

    def create_sql_schema(self):
        """
        Cria o esquema SQL para a tabela de destino.

        Este método cria a tabela e, se especificado, adiciona restrições de chave primária
        e colunas únicas, além de configurar a função e o gatilho para a coluna de data de modificação.

        Args:
            target_table (str): O nome da tabela de destino.
            target_schema (str): O esquema de destino onde a tabela será criada.
            **kwargs: Argumentos adicionais:
                - schema (str): Definição SQL da tabela quando schema_file_type='schema'.
        """
        logger.info(
            f"loader.create_sql_schema, target_table: {self.table.raw_model_name}, target_schema: {self.table.origin}"
        )

        self.create_table()

    def check_if_schema_exists(self):
        """
        Verifica se um schema existe no banco de dados.

        Este método consulta o catálogo do sistema para verificar se um schema
        com o nome especificado já existe no banco de dados.

        Args:
            target_schema (str): O nome do schema a ser verificado.

        Returns:
            bool: True se o schema existir, False caso contrário.
        """
        with self.engine.connect() as connection:
            # Consultas de leitura não precisam de transação explícita
            check_schema_query = text(
                f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{self.table.origin}'"
            )
            result = connection.execute(check_schema_query)

            # Fetch the first result
            schema_exists = result.fetchone() is not None

            if schema_exists:
                logger.info(f"Schema {self.table.origin} encontrado.")
            else:
                logger.info(f"Schema {self.table.origin} não existe.")

            return schema_exists

    def load_data(
        self,
        df: pd.DataFrame,
        mode="replace",
        chunksize=1000,
    ):
        """
        Carrega os dados de um DataFrame na tabela de destino.

        Este método verifica se a tabela existe e, se não existir, cria o esquema SQL.
        Em seguida, carrega os dados do DataFrame na tabela, podendo substituir os dados existentes.

        Args:
            df (pd.DataFrame): O DataFrame contendo os dados a serem carregados.
            target_table (str): O nome da tabela de destino.
            target_schema (str): O esquema de destino onde a tabela está localizada.
            mode (str): O modo de carregamento ('append' para adicionar, 'replace' para substituir).
            **kwargs: Argumentos adicionais:
                - chunksize (int): Tamanho dos blocos para carregamento em lotes.
                - table_definition (str): Definição SQL da tabela quando schema_file_type='schema'.
        """
        logger.debug(
            f"Iniciando load_data para {self.table.raw_model_name} em {self.table.origin}, modo: {self.table.extraction_strategy}"
        )

        schema_exists = self.check_if_schema_exists()

        # Se o schema não existe, cria o schema
        if schema_exists == False:
            logger.debug(f"Schema {self.table.origin} não existe, criando agora")
            self.create_schema(self.table.origin)

        # Verifica se a tabela existe no schema
        tables = inspect(self.engine).get_table_names(schema=self.table.origin)

        # Se a tabela existe no schema, carrega os dados
        if self.table.raw_model_name in tables:
            logger.debug(f"Tabela {self.table.raw_model_name} encontrada em {self.table.origin}")

            # Se o modo é replace, trunca a tabela para limpar os dados antes do insert
            if mode == "replace":
                logger.debug(f"Truncando dados de {self.table.raw_model_name}.")
                self.truncate_table()

        # Se a tabela não existe no schema, cria a tabela
        else:
            logger.debug(f"Tabela {self.table.raw_model_name} não encontrada em {self.table.origin}")

            if self.table_definition is None:
                raise ValueError(
                    "Relação não existe no destino, definição de tabela de destino precisa estar presente."
                )

            logger.debug(f"Criando tabela {self.table.raw_model_name} em {self.table.origin}")
            self.create_sql_schema()

        loaded_rows = 0
        logger.debug(f"Inserindo dados em {self.table.raw_model_name}")

        loaded_rows = df.to_sql(
            self.table.raw_model_name,
            con=self.engine,
            if_exists="append",
            schema=self.table.origin,
            index=False,
            chunksize=chunksize,
        )

        logger.debug(
            f"Fim do carregamento de dados em {self.table.raw_model_name}, {loaded_rows} linhas inseridas."
        )
