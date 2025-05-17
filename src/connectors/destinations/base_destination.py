"""
This module contains the abstract base class for loaders.
The loaders are responsible for loading data into various destinations,
such as databases, files, or other data stores.
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseLoader(ABC):
    """
    Abstract base class for data loaders.

    This class defines the interface that all loader implementations must follow.
    It provides abstract methods for common loader operations like loading data,
    creating schemas, and checking schema existence.
    """

    @abstractmethod
    def load_data(
        self,
        df: pd.DataFrame
    ):
        """
        Load data from a DataFrame into the target destination.

        Args:
            df (pd.DataFrame): The DataFrame containing the data to load.
            target_table (str): The name of the target table.
            target_schema (str): The schema where the table is located.
            mode (tuple, optional): The loading mode ('append' or 'replace').
            **kwargs: Additional arguments specific to the loader implementation.
        """
        pass

    @abstractmethod
    def create_schema(self, target_schema: str):
        """
        Create a new schema in the target destination.

        Args:
            target_schema (str): The name of the schema to create.
        """
        pass

    @abstractmethod
    def create_table(self, sql_command: str):
        """
        Create a new table using the provided SQL command.

        Args:
            sql_command (str): The SQL command to create the table.
        """
        pass

    @abstractmethod
    def check_if_schema_exists(self, target_schema: str) -> bool:
        """
        Check if a schema exists in the target destination.

        Args:
            target_schema (str): The name of the schema to check.

        Returns:
            bool: True if the schema exists, False otherwise.
        """
        pass
