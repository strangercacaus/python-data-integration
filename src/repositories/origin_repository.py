from typing import List, Optional
from src.database.connection import DatabaseConnection
from src.models.origin import Origin


class OriginRepository:
    def __init__(self):
        self.db = DatabaseConnection()

    def create(self, origin: Origin) -> Origin:
        query = """
        INSERT INTO "origin" (created_at, updated_at, name)
        VALUES (?, ?, ?)
        """
        params = (
            origin.created_at,
            origin.updated_at,
            origin.name,
        )
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            origin.id = cursor.lastrowid
            return origin

    def get_by_id(self, origin_id: int) -> Origin:
        query = """SELECT id, created_at, updated_at, name FROM "origin" WHERE id = ?"""
        result = self.db.execute_query(query, (origin_id,))
        if result:
            return Origin.from_dict(
                dict(
                    zip(
                        [
                            "id",
                            "created_at",
                            "updated_at",
                            "name",
                        ],
                        result[0],
                    )
                )
            )
        return None

    def get_all(self) -> List[Origin]:
        query = """SELECT id, created_at, updated_at, name FROM "origin" """
        results = self.db.execute_query(query)
        return [
            Origin.from_dict(
                dict(
                    zip(
                        [
                            "id",
                            "created_at",
                            "updated_at",
                            "name", 
                        ],
                        row,
                    )
                )
            )
            for row in results
        ]

    def update(self, origin: Origin) -> bool:
        query = """
        UPDATE "origin" 
        SET created_at = ?, updated_at = ?, name = ?
        WHERE id = ?
        """
        params = (
            origin.created_at,
            origin.updated_at,
            origin.name,
            origin.id,
        )
        return self.db.execute_update(query, params) > 0

    def delete(self, origin_id: int) -> bool:
        query = """DELETE FROM "origin" WHERE id = ?"""
        return self.db.execute_update(query, (origin_id,)) > 0
