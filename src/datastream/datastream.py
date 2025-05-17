import os
import pandas as pd
import logging

from ....datastream.base_datastream import Stream
from src.destinations.postgres_destination import PostgresLoader
from sources.notion_extractor import NotionDatabaseAPIExtractor

logger = logging.getLogger(__name__)


class NotionStream():

    def __init__(self, table):
        """Initialize NotionStream with the DataTable object containing configuration"""
        self.table = table

    def set_extractor(self):
        """Set the extractor for Notion API"""
        self.extractor = NotionDatabaseAPIExtractor(self.table)

    def extract_stream(self):
        """Extract data from Notion API and write to raw_layer

        Returns:
            DataFrame: The extracted data
        """
        logger.info("Extracting data from Notion API")
        if not self.extractor:
            self.set_extractor()
        return self.extractor.run()
    
    def set_table_definition(self, table_definition=None):
        """
        Set the table definition for this stream.

        Args:
            table_definition (str, optional): SQL DDL statement for table creation
        """
        if not table_definition:
            table_definition = self.table.schemaless_ddl

        self.table_definition = table_definition
        logger.info(f"Table definition set for {self.table.source_name}")

    def set_loader(self, engine):
        """
        Set up the PostgresLoader for this stream.

        Args:
            engine (sqlalchemy.engine.Engine): SQLAlchemy engine for database connection
        """
        self.loader = PostgresLoader(engine, self.table)
        self.loader.table_definition = self.table.schemaless_ddl
        logger.info(f"PostgreSQLLoader set for {self.table.source_name}")

    def load_stream(self, records, chunksize=None):
        """Load data into the target schema and table

        Args:
            data (DataFrame): DataFrame containing the data to be loaded
        """
        if not self.loader:
            raise ValueError("Loader not set. Call set_loader() first.")

        if not isinstance(records, pd.DataFrame):
            raise TypeError("Records must be a pandas DataFrame")

        logger.info(
            f"Loading {len(records)} records into {self.table.origin}.{self.table.raw_model_name}"
        )
        self.loader.load_data(df=records, chunksize=chunksize, mode="replace")
