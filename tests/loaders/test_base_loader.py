import pytest
import pandas as pd
from src.destinations.base_destination import BaseLoader


class TestBaseLoader:
    """Tests for the BaseLoader base class."""
    
    class ConcreteLoader(BaseLoader):
        """Concrete implementation of BaseLoader for testing."""
        
        def load_data(self, df, target_table, target_schema, mode="append", **kwargs):
            return f"Loaded {len(df)} rows into {target_schema}.{target_table} with mode {mode}"
        
        def create_schema(self, target_schema):
            return f"Created schema {target_schema}"
        
        def create_table(self, sql_command):
            return f"Created table with SQL: {sql_command}"
        
        def check_if_schema_exists(self, target_schema):
            return target_schema == "existing_schema"
    
    @pytest.fixture
    def loader(self):
        """Fixture for creating a ConcreteLoader instance."""
        return self.ConcreteLoader()
    
    @pytest.fixture
    def sample_df(self):
        """Fixture for creating a sample DataFrame."""
        return pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Test 1", "Test 2", "Test 3"]
        })
    
    def test_load_data(self, loader, sample_df):
        """Test the load_data method."""
        result = loader.load_data(
            df=sample_df,
            target_table="test_table",
            target_schema="test_schema"
        )
        assert result == "Loaded 3 rows into test_schema.test_table with mode append"
    
    def test_load_data_with_replace_mode(self, loader, sample_df):
        """Test the load_data method with replace mode."""
        result = loader.load_data(
            df=sample_df,
            target_table="test_table",
            target_schema="test_schema",
            mode="replace"
        )
        assert result == "Loaded 3 rows into test_schema.test_table with mode replace"
    
    def test_create_schema(self, loader):
        """Test the create_schema method."""
        result = loader.create_schema("new_schema")
        assert result == "Created schema new_schema"
    
    def test_create_table(self, loader):
        """Test the create_table method."""
        sql = "CREATE TABLE test_schema.test_table (id INTEGER, name TEXT)"
        result = loader.create_table(sql)
        assert result == f"Created table with SQL: {sql}"
    
    def test_check_if_schema_exists_true(self, loader):
        """Test the check_if_schema_exists method when schema exists."""
        result = loader.check_if_schema_exists("existing_schema")
        assert result is True
    
    def test_check_if_schema_exists_false(self, loader):
        """Test the check_if_schema_exists method when schema doesn't exist."""
        result = loader.check_if_schema_exists("non_existing_schema")
        assert result is False 