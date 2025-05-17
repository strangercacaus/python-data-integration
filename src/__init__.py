"""
BDT Data Integration package.

This package contains modules for extracting, transforming, and loading data
from various sources to PostgreSQL databases.
"""

# Import subpackages
from .datastream.datastream import *
from .sources import *
from .destinations import *
from .metadata import *
from .utils import *

__all__ = [
    'datastream',
    'sources',
    'destinations',
    'metadata',
    'utils'
]