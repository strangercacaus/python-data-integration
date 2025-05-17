import pytest
from abc import ABC, abstractmethod
from src.sources.base_source import GenericExtractor, GenericAPIExtractor, GenericDatabaseExtractor


class TestGenericExtractor:
    """Tests for the GenericExtractor base class."""
    
    def test_init(self):
        """Test initialization of GenericExtractor."""
        extractor = GenericExtractor("test_source")
        assert extractor.source == "test_source"


class TestGenericAPIExtractor:
    """Tests for the GenericAPIExtractor class."""
    
    class ConcreteAPIExtractor(GenericAPIExtractor):
        """Concrete implementation of GenericAPIExtractor for testing."""
        
        def _get_endpoint(self, **kwargs):
            return "https://api.example.com/endpoint"
        
        def fetch_paginated(self, **kwargs):
            return {"data": "test_data"}
        
        def run(self):
            return "test_run_result"
    
    def test_init(self):
        """Test initialization of GenericAPIExtractor."""
        extractor = self.ConcreteAPIExtractor("test_source", "test_token")
        assert extractor.origin == "test_source"
        assert extractor.token == "test_token"
    
    def test_abstract_methods(self):
        """Test that abstract methods are correctly defined."""
        # Verify that the class can be instantiated when abstract methods are implemented
        extractor = self.ConcreteAPIExtractor("test_source", "test_token")
        assert extractor._get_endpoint() == "https://api.example.com/endpoint"
        assert extractor.fetch_paginated() == {"data": "test_data"}
        assert extractor.run() == "test_run_result"


class TestGenericDatabaseExtractor:
    """Tests for the GenericDatabaseExtractor class."""
    
    class ConcreteDatabaseExtractor(GenericDatabaseExtractor):
        """Concrete implementation of GenericDatabaseExtractor for testing."""
        
        def _get_endpoint(self, **kwargs):
            return "postgresql://localhost:5432/test_db"
        
        def fetch_paginated(self, **kwargs):
            return {"data": "test_data"}
        
        def run(self):
            return "test_run_result"
    
    def test_init(self):
        """Test initialization of GenericDatabaseExtractor."""
        extractor = self.ConcreteDatabaseExtractor("test_source")
        assert extractor.source == "test_source"
    
    def test_abstract_methods(self):
        """Test that abstract methods are correctly defined."""
        # Verify that the class can be instantiated when abstract methods are implemented
        extractor = self.ConcreteDatabaseExtractor("test_source")
        assert extractor._get_endpoint() == "postgresql://localhost:5432/test_db"
        assert extractor.fetch_paginated() == {"data": "test_data"}
        assert extractor.run() == "test_run_result" 