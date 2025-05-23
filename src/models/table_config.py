from .column import Column
from .base import BaseModel
from typing import Dict, Any, List


class TableConfig(BaseModel):
    def __init__(
        self,
        source_name: str = None,
        source_identifier: str = None,
        target_name: str = None,
        target_schema: str = None,
        replication_strategy: str = None,
        days_interval: int = None,
        columns: List[Column] = None,
    ):
        super().__init__()
        self.source_name = source_name
        self.source_identifier = source_identifier
        self.target_name = target_name
        self.target_schema = target_schema
        self.replication_strategy = replication_strategy
        self.days_interval = days_interval
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

    def set_columns(self, columns: List[Column]):
        self.columns = columns

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "source_identifier": self.source_identifier,
            "target_name": self.target_name,
            "target_schema": self.target_schema,
            "replication_strategy": self.replication_strategy,
            "days_interval": self.days_interval,
            "columns": (
                [column.to_dict() for column in self.columns] if self.columns else []
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Table":
        return cls(
            source_name=data.get("source_name"),
            source_identifier=data.get("source_identifier"),
            target_name=data.get("target_name"),
            replication_strategy=data.get("replication_strategy"),
            days_interval=data.get("days_interval"),
            columns=[Column.from_dict(column) for column in data.get("columns", [])],
        )
