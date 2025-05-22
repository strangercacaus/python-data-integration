from typing import List, Optional
from src.database.connection import DatabaseConnection
from src.models.table import Table
from src.repositories.column_repository import ColumnRepository


class TableRepository:
    def __init__(self):
        self.db = DatabaseConnection()

    def create(self, table: Table) -> Table:
        query = """
        INSERT INTO "table" (created_at, updated_at, origin_id, source_name, source_identifier, target_name, active, replication_strategy, days_interval)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            table.created_at,
            table.updated_at,
            table.origin_id,
            table.source_name,
            table.source_identifier,
            table.target_name,
            table.active,
            table.replication_strategy,
            table.days_interval,
        )
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            table.id = cursor.lastrowid
            column_repository = ColumnRepository()
            table.columns = [column_repository.create(column) for column in table.columns]
            return table

    def get_by_id(self, table_id: int) -> Optional[Table]:
        query = "SELECT id, created_at, updated_at, origin_id, source_name, source_identifier, target_name, active, replication_strategy, days_interval, last_successful_sync_at, last_sync_attempt_at FROM table WHERE id = ?"
        result = self.db.execute_query(query, (table_id,))
        if result:
            return Table.from_dict(
                dict(
                    zip(
                        [
                            "id",
                            "created_at",
                            "updated_at",
                            "origin_id",
                            "source_name",
                            "source_identifier",
                            "target_name",
                            "active",
                            "replication_strategy",
                            "days_interval",
                            "last_successful_sync_at",
                            "last_sync_attempt_at",
                            "columns",
                        ],
                        result[0],
                    )
                )
            )
        return None

    def get_all(self) -> List[Table]:
        query = "SELECT id, created_at, updated_at, origin_id, source_name, source_identifier, target_name, active, replication_strategy, days_interval, last_successful_sync_at, last_sync_attempt_at FROM tables"
        results = self.db.execute_query(query)
        return [
            Table.from_dict(
                dict(
                    zip(
                        [
                            "id",
                            "created_at",
                            "updated_at",
                            "origin_id",
                            "source_name",
                            "source_identifier",
                            "target_name",
                            "active",
                            "replication_strategy",
                            "days_interval",
                            "last_successful_sync_at",
                            "last_sync_attempt_at",
                        ],
                        row,
                    )
                )
            )
            for row in results
        ]

    def update(self, table: Table) -> bool:
        query = """
        UPDATE table 
        SET  "created_at" = ?, "updated_at" = ?, "origin_id" = ?, "source_name" = ?, "source_identifier" = ?, "target_name" = ?, "active" = ?, "replication_strategy" = ?, "days_interval" = ?, "last_successful_sync_at" = ?, "last_sync_attempt_at" = ?,
        WHERE id = ?
        """
        params = (
            table.created_at,
            table.updated_at,
            table.origin_id,
            table.source_name,
            table.source_identifier,
            table.target_name,
            table.active,
            table.replication_strategy,
            table.days_interval,
            table.last_successful_sync_at,
            table.last_sync_attempt_at,
            table.id,
        )
        return self.db.execute_update(query, params) > 0

    def delete(self, table_id: int) -> bool:
        query = "DELETE FROM table WHERE id = ?"
        return self.db.execute_update(query, (table_id,)) > 0
