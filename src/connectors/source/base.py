import sys
import logging
from pathlib import Path
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

sys.path.append(str(Path(__file__).parent.parent))

from src.models.table_config import TableConfig

class BaseSource(ABC):
    """
    Classe abstrata que define um extrator de dados e os métodos obrigatórios.
    """

    def __init__(self, origin: str, table_config: TableConfig, *args, **kwargs) -> None:
        self.origin = origin
        self.table_config = table_config

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
