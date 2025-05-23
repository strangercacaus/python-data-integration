import logging
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from ..models.table_config import DataTable


class AppHelper:
    def __init__(self, connection):
        self.connection = connection

    def get_appdata(self):
        """Loads app data."""
        query = f"""SELECT *
        FROM public.table_configuration ct
        where ct.origin = '{self.origin}'"""

        engine = create_engine(
            self.db_url, poolclass=QueuePool, pool_size=5, max_overflow=10
        )
        with engine.connect() as connection:
            try:
                result = connection.execute(text(query))
                result_dataframe = pd.DataFrame(
                    result.fetchall(), columns=result.keys()
                )
                return [
                    DataTable(
                        id=row["id"],
                        origin=row["origin"],
                        source_name=row["source_name"],
                        source_identifier=row["source_identifier"],
                        target_name=row["target_name"],
                        active= bool(row["active"]),
                        unique_id_property=row["unique_id_property"],
                        updated_at_property=row["updated_at_property"],
                        extraction_strategy=row["extraction_strategy"],
                        materialization_strategy=row["materialization_strategy"],
                        days_interval= int(row["days_interval"]),
                        last_successful_sync_at=row["last_successful_sync_at"],
                        last_sync_attempt_at=row["last_sync_attempt_at"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        run_dbt_processed=bool(row["run_dbt_processed"]),
                        run_dbt_curated=bool(row["run_dbt_curated"]),
                        index_columns=row["index_columns"],
                    )
                    for row in result_dataframe.to_dict('records')
                ]
            except SQLAlchemyError as e:
                logger.error(f"Error loading table metadata: {e}")
                return None

    def update_table_configuration(
        self, value, source_name, last_successful_sync_at=None, last_sync_attempt_at=None
    ):
        """
        Update the table metadata with sync information.

        Args:
            id: The ID of the table configuration record
            source_name: Source name for logging purposes
            last_successful_sync_at: Last successful sync timestamp
            last_sync_attempt_at: Last attempt timestamp

        Returns:
            bool: True on success, False on failure
        """
        query = """
            UPDATE public.table_configuration
            SET
                last_successful_sync_at = COALESCE(:last_successful_sync_at, last_successful_sync_at),
                last_sync_attempt_at = COALESCE(:last_sync_attempt_at, last_sync_attempt_at)
            WHERE id = :id
        """

        # Convert NumPy types to native Python types to avoid adapter errors
        if hasattr(value, "item"):  # Check if it's a NumPy type with .item() method
            value = value.item()
        else:
            value = int(value) if value is not None else None

        params = {
            "id": value,
            "last_successful_sync_at": last_successful_sync_at,
            "last_sync_attempt_at": last_sync_attempt_at,
        }

        engine = create_engine(
            self.db_url, poolclass=QueuePool, pool_size=5, max_overflow=10
        )
        with engine.connect() as connection:
            try:
                connection.execute(text(query), params)
                logger.info(
                    f"Successfully updated metadata for {self.origin}.{source_name}"
                )
                return True
            except SQLAlchemyError as e:
                logger.error(f"Error updating metadata: {e}")
                return False
