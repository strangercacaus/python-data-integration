"""
Loader package for data integration.

This package contains loader classes for different data destinations.
The PostgresLoader class is responsible for loading data into PostgreSQL databases.
"""

from .base import BaseLoader
from .postgresql import PostgresLoader

__all__ = ['BaseLoader', 'PostgresLoader'] 