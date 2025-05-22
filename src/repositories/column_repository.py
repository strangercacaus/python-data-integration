from typing import List, Optional
from src.database.connection import DatabaseConnection
from src.models.column import Column


class ColumnRepository:
    def __init__(self):
        self.db = DatabaseConnection()

    def create(self, column: Column) -> Column:
        query = """
        INSERT INTO "column" (table_id, created_at, updated_at, name, type, active, primary, unique, indexed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            column.table_id,
            column.created_at,
            column.updated_at,
            column.name,
            column.type,
            column.active,
            column.primary,
            column.unique,
            column.indexed
        )
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            column.id = cursor.lastrowid
            return column

    def get_by_id(self, column_id: int) -> Column:
        query = """SELECT id, table_id, created_at, updated_at, name, type, active, primary, unique, indexed FROM "column" WHERE id = ?"""
        result = self.db.execute_query(query, (column_id,))
        if result:
            return Column.from_dict(
                dict(
                    zip(
                        [
                            "id",
                            "table_id",
                            "created_at",
                            "updated_at",
                            "name",
                            "type",
                            "active",
                            "primary",
                            "unique",
                            "indexed",
                        ],
                        result[0],
                    )
                )
            )
        return None
    
    def get_all_by_table_id(self, table_id: int) -> List[Column]:
        query = """SELECT id, table_id, created_at, updated_at, name, type, active, primary, unique, indexed FROM "column" WHERE table_id = ?"""
        results = self.db.execute_query(query, (table_id))
        if result:
            return [
                Column.from_dict(
                    dict(
                        zip(
                            [
                                "id",
                                "table_id",
                                "created_at",
                                "updated_at",
                                "name",
                                "type",
                                "active",
                                "primary",
                                "unique",
                                "indexed",
                            ],
                            row,
                        )
                    )
                )
                for row in results
            ]

    def get_all(self) -> List[Column]:
        query = """SELECT id, table_id, created_at, updated_at, name, type, active, primary, unique, indexed FROM "column" """
        results = self.db.execute_query(query)
        return [
            Column.from_dict(
                dict(
                    zip(
                        [
                            "id",
                            "table_id",
                            "created_at",
                            "updated_at",
                            "name",
                            "type",
                            "active",
                            "primary",
                            "unique",
                            "indexed",
                        ],
                        row,
                    )
                )
            )
            for row in results
        ]

    def update(self, column: Column) -> bool:
        query = """
        UPDATE "column" 
        SET table_id = ?, created_at = ?, updated_at = ?, name = ?, type = ?, active = ?, primary = ?, unique = ?, indexed = ?
        WHERE id = ?
        """
        params = (
            column.table_id,
            column.created_at,
            column.updated_at,
            column.name,
            column.type,
            column.active,
            column.primary,
            column.unique,
            column.indexed,
            column.id,
        )
        return self.db.execute_update(query, params) > 0

    def delete(self, column_id: int) -> bool:
        query = """DELETE FROM "column" WHERE id = ?"""
        return self.db.execute_update(query, (column_id,)) > 0
