import os
import sys
import logging
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.connectors.source.base import Source
from src.connectors.destination.base import Destination
from src.models.table_config import TableConfig

logger = logging.getLogger(__name__)


class Stream:

    def __init__(
        self, source: Source, destination: Destination, table_config: TableConfig
    ):
        self.table_config = table_config
        self.source = source
        self.destination = destination

    def get_source_columns(self):
        return self.source.get_columns()

    def get_destination_columns(self):
        return self.destination.get_columns()

    def extract(self):
        return self.source.run()

    def load(self, records, chunksize=None):
        self.destination.load_data(df=records, chunksize=chunksize, mode="replace")

    def prepare_destination_columns(self):

        errors = []

        source_columns = self.get_source_columns()
        destination_columns = self.get_destination_columns()

        for column in source_columns:

            if any(
                column.name == dest_col.name
                for dest_col in destination_columns.values()
            ):
                if not self.destination.assert_column_type(column.name, column.type):
                    try:
                        self.destination.alter_column(column)
                    except Exception as e:
                        column.active = False
                        errors.append(
                            {
                                "schema": table.schema,
                                "table": table.name,
                                "column": column.name,
                                "error": f"Não foi possível alterar o tipo da coluna {column.name} para {column.type}. Erro: {e}",
                            }
                        )
            else:
                self.destination.create_column(column)

        for column in source_columns:
            if column.active and column.indexed:
                try:
                    self.destination.create_index(column)
                except Exception as e:
                    column.active = False
                    errors.append(
                        {
                            "schema": table.schema,
                            "table": table.name,
                            "column": column.name,
                            "error": f"Não foi possível criar o índice da coluna {column.name}. Erro: {e}",
                        }
                    )

        if len(errors) > 0:
            text = "\n".join(
                [
                    f"Tabela: {error['Schema']}.{error['table']} - Coluna: {error['column']} - Erro: {error['error']}"
                    for error in errors
                ]
            )
            logger.error(
                f"{__class__.__name__} - Os seguintes erros ocorreram ao realizar o  ajuste de colunas: {text}"
            )

    def main(self):

        self.prepare_destination()
        records = self.extract()
        self.load(records, chunksize=None)
