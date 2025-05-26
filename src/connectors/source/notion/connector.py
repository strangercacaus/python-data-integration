import json
import logging
import requests
import pandas as pd
from typing import Dict, Any
from dotenv import load_dotenv
from datetime import datetime, timedelta

from src.connectors.source.base import BaseSource
from src.models.table_config import TableConfig

load_dotenv()

logger = logging.getLogger(__name__)


class NotionSource(BaseSource):

    def __init__(self, token, table_config: TableConfig):

        token = token
        super().__init__(origin="notion", table_config=table_config)
        self.base_url = "https://api.notion.com/v1"

    def _get_database_endpoint(self) -> str:

        return f"{self.base_url}/databases/{self.table.source_identifier}/query"

    def _get_headers(self):

        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2021-08-16",
            "Content-Type": "application/json",
        }

    def _get_next_payload(self, next_cursor=None, query_filter=None):
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        # Se query_filter foi fornecido, incorpore-o diretamente
        if query_filter and isinstance(query_filter, dict):
            # Merge the query_filter into the payload without nesting
            payload |= query_filter

        return payload

    def _extract_next_cursor(self, response):
        return response.get("next_cursor") if response.get("has_more") else None

    def run_get_request(self, url: str, headers: dict) -> Dict[str, Any]:
        if url and headers:
            response = requests.get(url, headers)
            response.raise_for_status()
            return response.status_code, response.json()

    def run_post_request(
        self, url: str, headers: dict, payload: dict
    ) -> Dict[str, Any]:

        if payload is None:
            payload = {}
        if url and headers:
            response = requests.post(url, headers, json=payload)
        response.raise_for_status()
        return response.json()

    def fetch_paginated_data(self, query_filter=None):

        next_cursor = None
        logger.info(f"Tentando obter dados de {self._get_endpoint()}")
        url = self._get_database_endpoint()
        headers = self._get_headers()
        successful_requests = 0
        while True:
            payload = self._get_next_payload(next_cursor, query_filter)
            response = self.run_post_request(url, headers, payload)
            response.raise_for_status()
            yield response["results"]
            successful_requests += 1
            logger.info(f"Página {successful_requests} obtida.")
            next_cursor = self._extract_next_cursor(response)
            if not next_cursor:
                break

    def run(self, days_interval: int = None):

        query_filter = None

        if type(days_interval) == int and days_interval > 0:
            start_date = datetime.now() - timedelta(days=days_interval)
            query_filter = {
                "filter": {
                    "timestamp": "last_edited_time",
                    "last_edited_time": {
                        "on_or_after": start_date.strftime("%Y-%m-%d")
                    },
                }
            }
        data = [
            {
                "ID": record.get("id"),
                "SUCCESS": True,
                "CONTENT": json.dumps(record),
            }
            for page in self.fetch_paginated_data(query_filter)
            for record in page
        ]

        if not data:
            return pd.DataFrame(columns=["ID", "SUCCESS", "CONTENT"])

        return pd.DataFrame(data, dtype=str)
