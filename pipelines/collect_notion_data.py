from pathlib import Path

from loguru import logger
from zenml import pipeline

from steps.collect_notion_data import (
    extract_notion_pages,
    extract_notion_pages_metadata,
    save_notion_pages,
)
from steps.infrastructure import upload_to_s3


@pipeline
def collect_notion_data(
    database_ids: list[str], output_dir: Path, to_s3: bool = False
) -> None:
    invocation_ids = []
    for database_id in database_ids:
        logger.info(f"Collecting pages from database '{database_id}'")
        pages_metadata = extract_notion_pages_metadata(database_id=database_id)
        pages_data = extract_notion_pages(pages_metadata=pages_metadata)

        result = save_notion_pages(
            database_id,
            pages=pages_data,
            output_dir=output_dir,
        )
        invocation_ids.append(result.invocation_id)

    if to_s3:
        upload_to_s3(folder_path=output_dir, after=invocation_ids)
