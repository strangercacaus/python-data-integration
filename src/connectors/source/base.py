import logging
from abc import ABC, abstractmethod 
from src.models.table import DataTable
logger = logging.getLogger(__name__)

class BaseSource(ABC):
    """
    Classe abstrata que define um extrator de dados e os métodos obrigatórios.
    """
    def __init__(
        self, origin: str, *args, **kwargs
    ) -> None:
        
        super().__init__(origin, *args, **kwargs)
        self.origin = origin

    @abstractmethod
    def fetch_paginated_data(self, **kwargs) -> dict:
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