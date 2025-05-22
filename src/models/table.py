from .column import Column
from .base import BaseModel
from typing import Dict, Any, List


class Table(BaseModel):
    def __init__(
        self,
        id: int = None,
        created_at: str = None,
        updated_at: str = None,
        origin_id: str = None,
        source_name: str = None,
        source_identifier: str = None,
        target_name: str = None,
        target_schema: str = None,
        active: bool = True,
        replication_strategy: str = None,
        days_interval: int = None,
        last_successful_sync_at: str = None,
        last_sync_attempt_at: str = None,
        columns: List[Column] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self.origin_id = origin_id
        self.source_name = source_name
        self.source_identifier = source_identifier
        self.target_name = target_name
        self.target_schema = target_schema
        self.active = active
        self.replication_strategy = replication_strategy
        self.days_interval = days_interval
        self.last_successful_sync_at = last_successful_sync_at
        self.last_sync_attempt_at = last_sync_attempt_at
        self.columns = columns

    @property
    def ddl(self) -> str:
        if not self.columns:
            raise ValueError("Uma tabela precisa de ao menos uma coluna")

        schema = f'"{self.target_schema}"' if self.target_schema else ""
        table = f'"{self.target_name}"'

        column_defs = []
        primary_keys = []
        unique_constraints = []

        for column in self.columns:
            column_defs.append(column.ddl)

            if column.primary:
                primary_keys.append(f'"{column.name}"')

            if column.unique:
                unique_constraints.append(f'"{column.name}"')

        if primary_keys:
            column_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")

        for unique_col in unique_constraints:
            column_defs.append(f"UNIQUE ({unique_col})")

        full_table_name = f"{schema}.{table}" if schema else table
        return f"""CREATE TABLE IF NOT EXISTS {full_table_name} (
    {',\n    '.join(column_defs)}
);"""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "origin_id": self.origin_id,
            "source_name": self.source_name,
            "source_identifier": self.source_identifier,
            "target_name": self.target_name,
            "active": self.active,
            "replication_strategy": self.replication_strategy,
            "days_interval": self.days_interval,
            "last_successful_sync_at": self.last_successful_sync_at,
            "last_sync_attempt_at": self.last_sync_attempt_at,
            "columns": (
                [column.to_dict() for column in self.columns] if self.columns else []
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Table":
        return cls(
            id=data.get("id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            origin_id=data.get("origin_id"),
            source_name=data.get("source_name"),
            source_identifier=data.get("source_identifier"),
            target_name=data.get("target_name"),
            active=data.get("active", True),
            replication_strategy=data.get("replication_strategy"),
            days_interval=data.get("days_interval"),
            last_successful_sync_at=data.get("last_successful_sync_at"),
            last_sync_attempt_at=data.get("last_sync_attempt_at"),
            columns=[Column.from_dict(column) for column in data.get("columns", [])],
        )
