import os
import pandas as pd
import logging

from .connectors.destination.postgresql import PostgreSQL
from .connectors.source.notion import Notion
from .app.job import Job

logger = logging.getLogger(__name__)


class Stream:

    def __init__(self, source: Source, destination: Destination, job: Job):
        """Initialize NotionStream with the DataTable object containing configuration"""
        self.source_id = source
        self.destination = destination
        self.job = job

    def extract_stream(self):
        return self.source.run()

    def load_stream(self, records, chunksize=None):
        self.destination.load_data(df=records, chunksize=chunksize, mode="replace")

    def main(self):
        records = self.extract_stream()
        self.load_stream(records, chunksize=None)
