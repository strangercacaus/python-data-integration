"""
Extractors package for data extraction in the ETL pipeline.

This package contains extractor classes for different data sources:
- GenericAPIExtractor: Abstract base class defining the interface for data extractors
- NotionDatabaseAPIExtractor: Extracts data from Notion API
- BenditoAPIExtractor: Extracts data from Bendito API
- BitrixAPIExtractor: Extracts data from Bitrix API

Each extractor class provides methods for:
- Handling API authentication
- Managing pagination
- Processing API responses
- Consolidating extracted data
"""

from .base_source import GenericAPIExtractor
from .notion.notion_extractor import NotionDatabaseAPIExtractor
from .bendito_extractor import BenditoAPIExtractor
from .bitrix_extractor import BitrixAPIExtractor

__all__ = [
    'GenericAPIExtractor',
    'NotionDatabaseAPIExtractor',
    'BenditoAPIExtractor',
    'BitrixAPIExtractor'
] 