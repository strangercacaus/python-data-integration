from typing import Dict, Any, Optional, List
from datetime import datetime
from .base import BaseModel

class Column(BaseModel):
    def __init__(
        self,
        id: int,
        table_id: int,
        created_at: datetime.time = None,
        updated_at: datetime.time = None,
        name: str = None,
        type: str = None,
        active: bool = True,
        primary: bool = False,
        unique: bool = False,
        indexed: bool = False,
    ):
        super().__init__(id, created_at, updated_at)
        self.table_id = table_id
        self.name = name
        self.type = type
        self.active = active
        self.primary = primary
        self.unique = unique
        self.indexed = indexed

    @property
    def ddl(self):
        return f"{self.name} {self.type}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "table_id": self.table_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "name": self.name,
            "type": self.type,
            "active": self.active,
            "primary": self.primary,
            "unique": self.unique,
            "indexed": self.indexed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Column':
        return cls(
            id=data.get("id"),
            table_id=data.get("table_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            name=data.get("name"),
            type=data.get("type"),
            active=data.get("active"),
            primary=data.get("primary"),
            unique=data.get("unique"),
            indexed=data.get("indexed")
        )