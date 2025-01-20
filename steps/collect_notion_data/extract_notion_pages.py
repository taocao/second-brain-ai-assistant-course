from typing_extensions import Annotated
from zenml import step

from second_brain.domain import Page, PageMetadata
from second_brain.infrastructure.notion import NotionPageClient


@step
def extract_notion_pages(
    pages_metadata: list[PageMetadata],
) -> Annotated[dict[str, Page], "pages"]:
    """Extract content from multiple Notion pages.

    Args:
        pages_metadata: List of page metadata to extract content from.

    Returns:
        dict[str, Page]: Dictionary mapping page IDs to their extracted content.
    """

    client = NotionPageClient()
    pages = {}
    for page_metadata in pages_metadata:
        pages[page_metadata.id] = client.extract_page(page_metadata)

    return pages
