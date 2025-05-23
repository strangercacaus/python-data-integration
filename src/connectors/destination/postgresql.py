import csv
import logging
import psycopg2

import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import (
    SQLAlchemyError,
    ObjectNotExecutableError,
)

from src.connectors.destination.base import BaseDestination
from src.models.table_config import TableConfig
from src.models.column import Column

logger = logging.getLogger("postgres_loader")


class PostgreSQLDestination(BaseDestination):

    def __init__(
        self,
        engine: Engine,
        table_config: TableConfig,
    ):
        super().__init__(engine=engine, table_config=table_config)

    def assert_schema_exists(self):
        with inspect(self.engine) as inspector:
            return self.table_config.target_schema in inspector.get_schema_names()

    def assert_table_exists(self):
        with inspect(self.engine) as inspector:
            return self.table_config.target_name in inspector.get_table_names(
                schema=self.table_config.target_schema
            )

    def get_columns(self):
        with inspect(self.engine) as inspector:
            columns = inspector.get_columns(
                self.table_config.target_name, schema=self.table_config.target_schema
            )
            return [
                Column.from_dict(
                    {
                        "name": column.name,
                        "type": column.type,
                        "primary": column.primary_key,
                        "nullable": column.nullable,
                    }
                )
                for column in columns
            ]

    def create_schema(self):
        with self.engine.begin() as connection:
            create_schema_query = text(
                f"CREATE SCHEMA {self.table_config.target_schema}"
            )
            connection.execute(create_schema_query)

    def create_table(self, ddl: str):
        with self.engine.begin() as connection:
            try:
                connection.execute(text(ddl))
            except SQLAlchemyError as e:
                if isinstance(e, ObjectNotExecutableError):
                    logger.error(
                        f"O comando SQL não é executável: {self.table.schemaless_ddl}"
                    )
                elif isinstance(e.orig, psycopg2.errors.DuplicateTable):
                    logger.error(f"{__name__}: A tabela já existe.")
                else:
                    logger.error(f"Um erro ocorreu: {e}")
                raise e

    def create_column(self, column: Column):
        with self.engine.begin() as connection:
            create_query = text("ALTER TABLE ?.? ADD COLUMN ? ? ?")
            nullable = "NULL" if column.nullable else "NOT NULL"
            connection.execute(
                create_query,
                [self.table_config.target_schema, self.table_config.target_name, column.name, column.type, column.nullable],
            )

    def alter_column_type(self, column: Column):
        with self.engine.begin() as connection:
            alter_query = text("ALTER TABLE ?.? ALTER COLUMN ? TYPE ?")
            connection.execute(
                alter_query,
                [self.table_config.target_schema, self.table_config.target_name, column.name, column.type],
            )
    
    def alter_column_nullable(self, column: Column):
        with self.engine.begin() as connection:
            alter_query = text("ALTER TABLE ?.? ALTER COLUMN ? SET ?")
            nullable = "NULL" if column.nullable else "NOT NULL"
            connection.execute(
                alter_query,
                [self.table_config.target_schema, self.table_config.target_name, column.name, nullable],
            )

    def truncate_table(self):
        with self.engine.begin() as connection:
            truncate_query = text(f"TRUNCATE TABLE ?.?")
            connection.execute(
                truncate_query,
                [self.table_config.target_schema, self.table_config.target_name],
            )

    def drop_schema(self):
        with self.engine.begin() as connection:
            drop_schema_query = text(f"DROP SCHEMA ?")
            connection.execute(drop_schema_query, [self.table_config.target_schema])

    def drop_table(self):
        with self.engine.begin() as connection:
            drop_query = text("DROP TABLE ?.?")
            connection.execute(
                drop_query,
                [self.table_config.target_schema, self.table_config.target_name],
            )

    def drop_column(self, column: Column):
        with self.engine.begin() as connection:
            drop_query = text("ALTER TABLE ?.? DROP COLUMN ?")
            connection.execute(
                drop_query,
                [
                    self.table_config.target_schema,
                    self.table_config.target_name,
                    column.name,
                ],
            )

    def create_constraint(self):
        pass

    def load_data(
        self,
        df: pd.DataFrame,
        mode="replace",
        chunksize=1000,
    ):

        schema_exists = self.check_if_schema_exists()

        if schema_exists == False:
            self.create_schema(self.table.origin)

        tables = inspect(self.engine).get_table_names(schema=self.table.origin)

        if self.table.raw_model_name in tables:

            if mode == "replace":
                logger.debug(f"Truncando dados de {self.table.raw_model_name}.")
                self.truncate_table()

        else:
            logger.debug(
                f"Tabela {self.table.raw_model_name} não encontrada em {self.table.origin}"
            )

            if self.table_definition is None:
                raise ValueError(
                    "Relação não existe no destino, definição de tabela de destino precisa estar presente."
                )

            logger.debug(
                f"Criando tabela {self.table.raw_model_name} em {self.table.origin}"
            )
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
