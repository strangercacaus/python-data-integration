import os
import sys
from pathlib import Path
from sqlalchemy import create_engine

sys.path.append(str(Path(__file__).parent.parent))

from src.connectors.source.notion import NotionSourceConnector
from src.connectors.destination.postgresql import PostgreSQL
from src.models.table_config import TableConfig
from src.stream.stream import Stream

load_dotenv()


def main(
    source_name: str,
    source_identifier: str,
    target_name: str,
    target_schema: str,
    replication_strategy: str,
    days_interval: int,
):

    table_config = TableConfig(
        source_name=source_name,
        source_identifier=source_identifier,
        target_name=target_name,
        target_schema=target_schema,
        replication_strategy=replication_strategy,
        days_interval=days_interval,
    )

    source = NotionSourceConnector(
        token=os.getenv("NOTION_TOKEN"), table_config=table_config
    )

    engine = create_engine(os.getenv("DATABASE_URL"))
    destination = PostgreSQL(engine=engine)

    stream = Stream(source=source, destination=destination, table_config=table_config)

    stream.main()
