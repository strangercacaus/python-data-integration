from .base import BaseModel
from typing import Dict, Any
from datetime import datetime


class Job(BaseModel):
    def __init__(
        self,
        id: int,
        created_at: datetime.time,
        updated_at: datetime.time,
        origin_id: int,
        table_id: int,
        started_extraction_at: datetime.time,
        finished_extraction_at: datetime.time,
        started_sync_at: datetime.time,
        finished_sync_at: datetime.time,
        tables_to_process: int,
        tables_processed: int,
        rows_extracted: int,
        rows_loaded: int,
        status: str,
    ):
        super().__init__(id, created_at, updated_at)
        self.origin_id = origin_id
        self.table_id = table_id
        self.started_extraction_at = started_extraction_at
        self.finished_extraction_at = finished_extraction_at
        self.started_sync_at = started_sync_at
        self.finished_sync_at = finished_sync_at
        self.tables_to_process = tables_to_process
        self.tables_processed = tables_processed
        self.rows_extracted = rows_extracted
        self.rows_loaded = rows_loaded
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "origin_id": self.origin_id,
            "table_id": self.table_id,
            "started_extraction_at": self.started_extraction_at,
            "finished_extraction_at": self.finished_extraction_at,
            "started_sync_at": self.started_sync_at,
            "finished_sync_at": self.finished_sync_at,
            "tables_to_process": self.tables_to_process,
            "tables_processed": self.tables_processed,
            "rows_extracted": self.rows_extracted,
            "rows_loaded": self.rows_loaded,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        return cls(
            id=data.get("id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            origin_id=data.get("origin_id"),
            table_id=data.get("table_id"),
            started_extraction_at=data.get("started_extraction_at"),
            finished_extraction_at=data.get("finished_extraction_at"),
            started_sync_at=data.get("started_sync_at"),
            finished_sync_at=data.get("finished_sync_at"),
            tables_to_process=data.get("tables_to_process"),
            tables_processed=data.get("tables_processed"),
            rows_extracted=data.get("rows_extracted"),
            rows_loaded=data.get("rows_loaded"),
            status=data.get("status"),
        )
