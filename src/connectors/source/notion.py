import os
import json
import logging
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
from .base import GenericAPIExtractor

load_dotenv()

logger = logging.getLogger(__name__)


class NotionDatabaseAPIExtractor(GenericAPIExtractor):
    """
    Extrator para a extração de dados da API Database Query do Notion.

    Atributos:
        - base_endpoint (str): URL base da API do Notion, 'https://api.notion.com/v1'.
        - database_id (str): ID do banco de dados do Notion.
        - token (str): Bearer Token da conta conectada à integração.
    """

    def __init__(self, table):
        """
        Inicializa um extrator para a API do Notion.

        Args:
            table (DataTable): Objeto DataTable com as configurações da fonte
        """
        token = os.environ.get("NOTION_APIKEY")
        super().__init__(table, token=token)
        self.base_url = "https://api.notion.com/v1/databases"

    def _get_endpoint(self) -> str:
        """
        Obtém o endpoint para a consulta do banco de dados do Notion.

        Returns:
            str: O endpoint formatado para a consulta do banco de dados.
        """
        return f"{self.base_url}/{self.table.source_identifier}/query"

    def _get_headers(self):
        """
        Obtém os cabeçalhos necessários para as requisições à API do Notion.

        Returns:
            dict: Um dicionário contendo os cabeçalhos de autorização e conteúdo.
        """
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2021-08-16",
            "Content-Type": "application/json"
        }

    def _get_next_payload(self, next_cursor=None, query_filter=None):
        """
        Gera o payload para a próxima requisição, incluindo o cursor de início.

        Args:
            next_cursor (str, optional): O cursor para a próxima página de resultados.
            query_filter (dict, optional): Filtro de consulta a ser aplicado.

        Returns:
            dict: O payload para a próxima requisição.
        """
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        # Se query_filter foi fornecido, incorpore-o diretamente
        if query_filter and isinstance(query_filter, dict):
            # Merge the query_filter into the payload without nesting
            payload |= query_filter

        return payload

    def _extract_next_cursor(self, response):
        """
        Extrai o próximo cursor da resposta da API.

        Args:
            response (dict): A resposta da API contendo informações de paginação.

        Returns:
            str: O próximo cursor, se disponível; caso contrário, None.
        """
        return response.get("next_cursor") if response.get("has_more") else None

    def get_data(self) -> tuple[int, any]:
        """
        Realiza uma chamada GET à API do Notion para obter dados.

        Returns:
            tuple[int, any]: Um tupla contendo o código de status e os dados retornados.
        """
        endpoint = self._get_endpoint()
        headers = self._get_headers()
        logger.info(f"Enviando requisição GET para {endpoint}")
        response = requests.get(url=endpoint, headers=headers)
        response.raise_for_status()
        return response.status_code, response.json()

    def post_data(self, payload=None):
        """
        Realiza uma chamada POST à API do Notion.

        Args:
            payload (dict, optional): O corpo da requisição em formato JSON.

        Returns:
            dict: Os dados retornados pela API.
        """
        if payload is None:
            payload = {}
        endpoint = self._get_endpoint()
        headers = self._get_headers()

        response = requests.post(url=endpoint, headers=headers, json=payload)
        response.raise_for_status()

        return response.json()

    def fetch_paginated(self, query_filter=None):
        """
        Obtém dados paginados da API do Notion.

        Args:
            query_filter (dict, optional): Filtro de consulta a ser aplicado.

        Yields:
            list: Um gerador que produz os resultados de cada página.
        """
        successful_requests = 0
        next_cursor = None
        logger.info(f"Tentando obter dados de {self._get_endpoint()}")
        while True:
            payload = self._get_next_payload(next_cursor, query_filter)
            response = self.post_data(payload=payload)
            successful_requests += 1
            logger.info(f"Página {successful_requests} obtida.")
            yield response["results"]
            next_cursor = self._extract_next_cursor(response)
            if not next_cursor:
                break

    def run(self):
        """
        Executa a rotina principal do extrator, consolidando os dados extraídos.

        Returns:
            DataFrame: Um DataFrame com as colunas ID, SUCCESS e CONTENT
        """
        query_filter = None
        if self.table.days_interval > 0:
            start_date = datetime.now() - timedelta(days=self.table.days_interval)
            query_filter = {
                "filter": {
                    "timestamp": "last_edited_time",
                    "last_edited_time": {"on_or_after": start_date.strftime("%Y-%m-%d")},
                }
            }
        data = [
            {
                "ID": record.get("id"),
                "SUCCESS": True,
                "CONTENT": json.dumps(record),
            }
            for page in self.fetch_paginated(query_filter)
            for record in page
        ]
        
        if not data:
            return pd.DataFrame(columns=["ID", "SUCCESS", "CONTENT"])
            
        return pd.DataFrame(data, dtype=str)
