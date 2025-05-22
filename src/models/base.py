from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime


class BaseModel(ABC):
    def __init__(
        self, id: int, created_at: datetime.time = None, updated_at: datetime.time = None
    ):
        self.id = id
        self.created_at = datetime.now() if created_at is None else created_at
        self.updated_at = datetime.now() if updated_at is None else updated_at

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Create model instance from dictionary"""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
