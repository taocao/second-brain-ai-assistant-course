from pathlib import Path

from loguru import logger
from zenml import pipeline

from steps.collect_notion_data import (
    extract_notion_documents,
    extract_notion_documents_metadata,
)
from steps.infrastructure import save_documents_to_disk, upload_to_s3


@pipeline
def collect_notion_data(
    database_ids: list[str], data_dir: Path, to_s3: bool = False
) -> None:
    notion_data_dir = data_dir / "notion"
    notion_data_dir.mkdir(parents=True, exist_ok=True)

    invocation_ids = []
    for index, database_id in enumerate(database_ids):
        logger.info(f"Collecting pages from database '{database_id}'")
        documents_metadata = extract_notion_documents_metadata(database_id=database_id)
        documents_data = extract_notion_documents(documents_metadata=documents_metadata)

        result = save_documents_to_disk(
            documents=documents_data,
            output_dir=notion_data_dir / f"database_{index}",
        )
        invocation_ids.append(result.invocation_id)

    if to_s3:
        upload_to_s3(
            folder_path=notion_data_dir,
            s3_prefix="second_brain_course/notion",
            after=invocation_ids,
        )
