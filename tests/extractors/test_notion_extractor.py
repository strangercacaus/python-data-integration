import json
import pytest
from unittest.mock import patch, MagicMock, call
import pandas as pd
from src.sources.notion_extractor import NotionDatabaseAPIExtractor


class TestNotionDatabaseAPIExtractor:
    """Tests for the NotionDatabaseAPIExtractor class."""
    
    @pytest.fixture
    def notion_extractor(self):
        """Fixture for creating a NotionDatabaseAPIExtractor instance."""
        return NotionDatabaseAPIExtractor(
            token="test_token",
            database_id="test_database_id"
        )
    
    def test_init(self, notion_extractor):
        """Test initialization of NotionDatabaseAPIExtractor."""
        assert notion_extractor.source == "notion"
        assert notion_extractor.token == "test_token"
        assert notion_extractor.database_id == "test_database_id"
        assert notion_extractor.base_endpoint == "https://api.notion.com/v1/databases"
    
    def test_get_endpoint(self, notion_extractor):
        """Test the _get_endpoint method."""
        expected_endpoint = f"{notion_extractor.base_endpoint}/{notion_extractor.database_id}/query"
        assert notion_extractor._get_endpoint() == expected_endpoint
    
    def test_get_headers(self, notion_extractor):
        """Test the _get_headers method."""
        headers = notion_extractor._get_headers()
        assert headers["Authorization"] == f"Bearer {notion_extractor.token}"
        assert headers["Notion-Version"] == "2021-08-16"
        assert headers["Content-Type"] == "application/json"
        assert headers["Data"] == "{}"
    
    def test_get_next_payload_with_cursor(self, notion_extractor):
        """Test the _get_next_payload method with a cursor."""
        payload = notion_extractor._get_next_payload("test_cursor")
        assert payload == {"start_cursor": "test_cursor"}
    
    def test_get_next_payload_without_cursor(self, notion_extractor):
        """Test the _get_next_payload method without a cursor."""
        payload = notion_extractor._get_next_payload()
        assert payload == {}
    
    def test_extract_next_cursor_with_more(self, notion_extractor):
        """Test extracting the next cursor from a response with more results."""
        response = {"has_more": True, "next_cursor": "test_cursor"}
        assert notion_extractor._extract_next_cursor_from_response(response) == "test_cursor"
    
    def test_extract_next_cursor_without_more(self, notion_extractor):
        """Test extracting the next cursor from a response without more results."""
        response = {"has_more": False, "next_cursor": "test_cursor"}
        assert notion_extractor._extract_next_cursor_from_response(response) is None
    
    @patch("requests.get")
    def test_get_data(self, mock_get, notion_extractor):
        """Test the get_data method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [{"id": "test_id"}]}
        mock_get.return_value = mock_response
        
        # Call the method
        status_code, data = notion_extractor.get_data()
        
        # Assertions
        mock_get.assert_called_once_with(
            url=notion_extractor._get_endpoint(),
            headers=notion_extractor._get_headers()
        )
        assert status_code == 200
        assert data == {"results": [{"id": "test_id"}]}
    
    @patch("requests.post")
    def test_post_data(self, mock_post, notion_extractor):
        """Test the post_data method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [{"id": "test_id"}]}
        mock_post.return_value = mock_response
        
        # Call the method
        data = notion_extractor.post_data(payload={"test": "payload"})
        
        # Assertions
        mock_post.assert_called_once_with(
            url=notion_extractor._get_endpoint(),
            headers=notion_extractor._get_headers(),
            json={"test": "payload"}
        )
        assert data == {"results": [{"id": "test_id"}]}
    
    def test_fetch_paginated(self, notion_extractor, mocker):
        """Test the fetch_paginated method."""
        # Mock the post_data method
        responses = [
            {"results": [{"id": "1"}, {"id": "2"}], "has_more": True, "next_cursor": "cursor1"},
            {"results": [{"id": "3"}, {"id": "4"}], "has_more": False, "next_cursor": None}
        ]
        mocker.patch.object(
            notion_extractor, 'post_data', 
            side_effect=responses
        )
        
        # Call the method and collect the results
        results = list(notion_extractor.fetch_paginated())
        
        # Assertions
        assert len(results) == 2
        assert results[0] == [{"id": "1"}, {"id": "2"}]
        assert results[1] == [{"id": "3"}, {"id": "4"}]
        
        # Assert correct payloads were used
        expected_calls = [
            call(payload={}),
            call(payload={"start_cursor": "cursor1"})
        ]
        notion_extractor.post_data.assert_has_calls(expected_calls)
    
    def test_run_with_schemaless(self, notion_extractor, mocker):
        """Test the run method with schemaless=True."""
        # Setup mock for fetch_paginated
        mock_results = [
            [{"id": "1", "title": "Test 1"}],
            [{"id": "2", "title": "Test 2"}]
        ]
        mocker.patch.object(
            notion_extractor, 'fetch_paginated', 
            return_value=mock_results
        )
        
        # Call the method
        result = notion_extractor.run(schemaless=True)
        
        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ['ID', 'SUCCESS', 'CONTENT']
        assert result['ID'].tolist() == ['1', '2']
        assert all(result['SUCCESS'])
        assert json.loads(result['CONTENT'].iloc[0]) == {"id": "1", "title": "Test 1"}
        assert json.loads(result['CONTENT'].iloc[1]) == {"id": "2", "title": "Test 2"}
    
    def test_run_without_schemaless(self, notion_extractor, mocker):
        """Test the run method with schemaless=False."""
        # Setup mock for fetch_paginated
        mock_results = [
            [{"id": "1", "title": "Test 1"}],
            [{"id": "2", "title": "Test 2"}]
        ]
        mocker.patch.object(
            notion_extractor, 'fetch_paginated', 
            return_value=mock_results
        )
        
        # Call the method
        result = notion_extractor.run(schemaless=False)
        
        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result.iloc[0]['id'] == '1'
        assert result.iloc[0]['title'] == 'Test 1'
        assert result.iloc[1]['id'] == '2'
        assert result.iloc[1]['title'] == 'Test 2' 