from typing_extensions import Annotated
from zenml import step

from second_brain.domain import DocumentMetadata
from second_brain.infrastructure.notion import NotionDatabaseClient


@step
def extract_notion_documents_metadata(
    database_id: str,
) -> Annotated[list[DocumentMetadata], "notion_documents_metadata"]:
    """Extract metadata from Notion documents in a specified database.

    Args:
        database_id: The ID of the Notion database to query.

    Returns:
        A list of DocumentMetadata objects containing the extracted information.
    """

    client = NotionDatabaseClient()
    documents_metadata = client.query_notion_database(database_id)

    return documents_metadata
