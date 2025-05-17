import logging
from abc import ABC, abstractmethod 
from metadata.data_table import DataTable
logger = logging.getLogger(__name__)

class GenericExtractor(ABC):
    """
    Classe abstrata que define um extrator de dados e os métodos obrigatórios.
    """
    def __init__(
        self, origin: str, token, *args, **kwargs
    ) -> None:
        """
        Inicializa um objeto da classe GenericAPIExtractor.

        Args:
            identifier (str): String que identifica a API.
            token: O token de autenticação utilizado nesta API.
            writer: O objeto responsável por gravar os dados extraídos.
            **kwargs: Argumentos adicionais para configuração do extrator.
        """
        super().__init__(origin, *args, **kwargs)
        self.origin = origin
        self.token = token

    @abstractmethod
    def _get_endpoint(self, **kwargs) -> str:
        """
        Método abstrato para obter o endpoint do extrator.

        Returns:
            str: O endpoint da API.
        """
        pass

    @abstractmethod
    def fetch_paginated(self, **kwargs) -> dict:
        """
        Método abstrato para implementar a lógica de paginação.

        Returns:
            dict: Um dicionário contendo os dados paginados extraídos.
        """
        pass
    
    @abstractmethod
    def run():
        """
        Método abstrato para implementar a rotina principal do extrator.
        
        Este método deve retornar todos os dados extraídos do extrator, 
        consolidados em um único objeto.

        Returns:
            any: Os dados extraídos consolidados.
        """
        pass 