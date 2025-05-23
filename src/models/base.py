from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModel(ABC):
    def __init__(self):
        pass

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
        return f"{self.__class__.__name__}"
