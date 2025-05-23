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

    def prepare_destination(self):

        if not self.destination.assert_schema_exists():
            self.destination.create_schema()

        if not self.destination.assert_table_exists():
            self.destination.create_table()
        else:
            source_columns = self.get_source_columns()
            destination_columns = self.get_destination_columns()
            for source_column in source_columns:

                if source_column.name not in destination_columns.name:
                    self.destination.create_column(source_column)
                elif not source_column.equals(destination_columns[source_column]):
                    if source_column.nullable != destination_columns[source_column.name].nullable:
                        self.destination.update_column(source_column)

    def main(self):

        self.prepare_destination()

        records = self.extract()
        self.load(records, chunksize=None)
