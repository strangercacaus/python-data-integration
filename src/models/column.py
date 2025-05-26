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
        nullable: bool = True,
        unique: bool = False,
        indexed: bool = False,
    ):
        super().__init__()
        self.name = name
        self.type = type
        self.active = active
        self.primary = primary
        self.nullable = nullable
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
            "nullable": self.nullable,
            "unique": self.unique,
            "indexed": self.indexed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Column':
        return cls(
            name=data.get("name"),
            type=data.get("type"),
            active=data.get("active"),
            primary=data.get("primary"),
            nullable=data.get("nullable"),
            unique=data.get("unique"),
            indexed=data.get("indexed")
        )
    
    def equals(self, other: 'Column') -> bool:
        if self.name == other.name and self.type == other.type and self.primary == other.primary and self.nullable == other.nullable:
            return {"Result": True, "Value": None}
        else:
            diffs = {}
            if self.name != other.name:
                diffs["name"] = {"Self": self.name, "Other": other.name}
            if self.type != other.type:
                diffs["type"] = {"Self": self.type, "Other": other.type}
            if self.primary != other.primary:
                diffs["primary"] = {"Self": self.primary, "Other": other.primary}
            if self.nullable != other.nullable:
                diffs["nullable"] = {"Self": self.nullable, "Other": other.nullable}
            return {"Result": False, "Value": diffs}
