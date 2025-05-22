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
    ObjectNotExecutableError,
)

from utils import Utils
from destinations.base import BaseDestination
from src.models.table import DataTable

# Create a named logger for this module
logger = logging.getLogger("postgres_loader")


class PostgreSQL(BaseDestination):

    def __init__(
        self,
        engine: Engine = None,
    ):
        self.engine = engine
        
    def read_structure(self):
        pass

    def create_schema(self):
        with self.engine.begin() as connection:
            create_schema_query = text(f"CREATE SCHEMA {self.table.origin}")
            connection.execute(create_schema_query)

    def create_table(self):
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
    
    def create_column(self):
        pass

    def truncate_table(self):
        with self.engine.begin() as connection:
            truncate_query = text(f"TRUNCATE TABLE {self.table.origin}.{self.table.raw_model_name}")
            connection.execute(truncate_query)
    
    def drop_schema(self):
        pass

    def drop_table(self):
        with self.engine.begin() as connection:
            drop_query = text(f"DROP TABLE {self.table.origin}.{self.table.raw_model_name}")
            connection.execute(drop_query)

    def drop_column(self):
        pass

    def load_data(
        self,
        df: pd.DataFrame,
        mode="replace",
        chunksize=1000,
    ):
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
