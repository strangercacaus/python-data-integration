"""
This module contains the abstract base class for loaders.
The loaders are responsible for loading data into various destinations,
such as databases, files, or other data stores.
"""
import sys
from pathlib import Path
from abc import ABC, abstractmethod
from sqlalchemy import Engine

sys.path.append(str(Path(__file__).parent.parent))

from src.models.table_config import TableConfig

class BaseDestination(ABC):
    def __init__(self, engine: Engine, table_config: TableConfig):
        self.engine = engine
        self.table_config = table_config

    @abstractmethod
    def assert_schema_exists(self):
        pass

    @abstractmethod
    def assert_table_exists(self):
        pass

    @abstractmethod
    def get_columns(self):
        pass

    @abstractmethod
    def create_schema(self):
        pass

    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def create_column(self):
        pass

    @abstractmethod
    def truncate_table(self):
        pass

    @abstractmethod
    def drop_schema(self):
        pass

    @abstractmethod
    def drop_table(self):
        pass

    @abstractmethod
    def drop_column(self):
        pass

    @abstractmethod
    def create_constraint(self):
        pass

    @abstractmethod
    def load_data(self):
        pass