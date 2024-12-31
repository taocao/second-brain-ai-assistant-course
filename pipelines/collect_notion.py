from loguru import logger
from zenml import pipeline

from steps.collect_notion import (
    extract_notion_pages,
    extract_notion_pages_metadata,
    save_notion_pages,
)


@pipeline
def collect_notion(database_ids: list[str]) -> None:
    for database_id in database_ids:
        logger.info(f"Collecting pages from database '{database_id}'")
        page_ids = extract_notion_pages_metadata(database_id=database_id)
        pages_data = extract_notion_pages(page_ids=page_ids)
        save_notion_pages(database_id, pages=pages_data)
