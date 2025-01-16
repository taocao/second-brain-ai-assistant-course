from typing_extensions import Annotated
from zenml import step

from second_brain.entities import PageMetadata
from second_brain.infrastructure.notion import NotionDatabaseClient


@step
def extract_notion_pages_metadata(
    database_id: str,
) -> Annotated[list[PageMetadata], "notion_pages_metadata"]:
    """Extract metadata from Notion pages in a specified database.

    Args:
        database_id: The ID of the Notion database to query.

    Returns:
        A list of PageMetadata objects containing the extracted information.
    """

    client = NotionDatabaseClient()
    pages_metadata = client.query_notion_database(database_id)

    return pages_metadata
