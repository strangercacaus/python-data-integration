from .column import Column
from .base import BaseModel
from .table import Table
from typing import Dict, Any, List
from datetime import datetime


class Origin(BaseModel):
    def __init__(
        self,
        id: int = None,
        created_at: datetime.time = None,
        updated_at: datetime.time = None,
        name: str = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Origin":
        return cls(
            id=data.get("id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            name=data.get("name")
        )
