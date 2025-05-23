from typing import Dict, Any, Optional, List
from datetime import datetime
from .base import BaseModel


class Column(BaseModel):
    def __init__(
        self,
        name: str = None,
        type: str = None,
        active: bool = True,
        primary: bool = False,
        unique: bool = False,
        indexed: bool = False,
    ):
        super().__init__()
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
            "name": self.name,
            "type": self.type,
            "active": self.active,
            "primary": self.primary,
            "unique": self.unique,
            "indexed": self.indexed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Column":
        return cls(
            name=data.get("name"),
            type=data.get("type"),
            active=data.get("active"),
            primary=data.get("primary"),
            unique=data.get("unique"),
            indexed=data.get("indexed"),
        )

    def equals(self, other: "Column") -> bool:
        return (
            self.name == other.name
            and self.type == other.type
            and self.active == other.active
            and self.primary == other.primary
            and self.unique == other.unique
            and self.indexed == other.indexed
        )
