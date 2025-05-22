"""
This module contains the abstract base class for loaders.
The loaders are responsible for loading data into various destinations,
such as databases, files, or other data stores.
"""

from abc import ABC, abstractmethod
from pandas import DataFrame

class BaseDestination(ABC):
    
    @abstractmethod
    def read_structure(self):
        pass
    
    @abstractmethod
    def create_schema(self, schema: str):
        pass

    @abstractmethod
    def create_table(self, schema: str, table: str):
        pass
    
    @abstractmethod
    def create_column(self, schema: str, table: str, column: str):
        pass
    
    @abstractmethod
    def truncate_table(self, schema, table: str):
        pass
    
    @abstractmethod
    def drop_schema(self, schema: str):
        pass
    
    @abstractmethod
    def drop_table(self, schema: str, table: str):
        pass
        
    @abstractmethod
    def drop_column(self, schema: str, table:str, column: str):
        pass
    
    @abstractmethod
    def load_data(self, df: DataFrame):
        pass