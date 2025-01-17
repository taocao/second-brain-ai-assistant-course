from zenml import pipeline

from steps.infrastructure import (
    fetch_from_mongodb,
)


@pipeline
def generate_dataset(limit: int = 100, extract_collection_name: str = "raw_data") -> None:
    fetch_from_mongodb(limit=limit, collection_name=extract_collection_name)
