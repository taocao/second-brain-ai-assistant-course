from pathlib import Path

from loguru import logger
from zenml import pipeline

from steps.etl import add_quality_score, crawl
from steps.infrastructure import (
    ingest_to_mongodb,
    read_documents_from_disk,
    save_documents_to_disk,
    upload_to_s3,
)


@pipeline
def etl(
    data_dir: Path,
    load_collection_name: str,
    to_s3: bool = False,
    max_workers: int = 10,
    quality_agent_model_id: str = "gpt-4o-mini",
    quality_agent_mock: bool = True,
) -> None:
    notion_data_dir = data_dir / "notion"
    logger.info(f"Reading notion data from {notion_data_dir}")
    crawled_data_dir = data_dir / "crawled"
    logger.info(f"Saving crawled data to {crawled_data_dir}")

    documents = read_documents_from_disk(
        data_directory=notion_data_dir, nesting_level=1
    )
    crawled_documents = crawl(documents=documents, max_workers=max_workers)
    enhanced_documents = add_quality_score(
        documents=crawled_documents,
        model_id=quality_agent_model_id,
        mock=quality_agent_mock,
        max_workers=max_workers,
    )

    save_documents_to_disk(documents=enhanced_documents, output_dir=crawled_data_dir)
    if to_s3:
        upload_to_s3(
            folder_path=crawled_data_dir,
            s3_prefix="second_brain_course/crawled",
            after="save_documents_to_disk",
        )
    ingest_to_mongodb(
        models=enhanced_documents,
        collection_name=load_collection_name,
        clear_collection=True,
    )
