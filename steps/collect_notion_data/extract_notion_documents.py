from typing_extensions import Annotated
from zenml import step

from second_brain.domain import Document, DocumentMetadata
from second_brain.infrastructure.notion import NotionDocumentClient


@step
def extract_notion_documents(
    documents_metadata: list[DocumentMetadata],
) -> Annotated[dict[str, Document], "documents"]:
    """Extract content from multiple Notion documents.

    Args:
        documents_metadata: List of document metadata to extract content from.

    Returns:
        dict[str, Document]: Dictionary mapping document IDs to their extracted content.
    """

    client = NotionDocumentClient()
    documents = {}
    for document_metadata in documents_metadata:
        documents[document_metadata.id] = client.extract_document(document_metadata)

    return documents
