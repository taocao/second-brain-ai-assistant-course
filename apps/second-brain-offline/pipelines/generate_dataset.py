from zenml import pipeline

from steps.infrastructure import (
    fetch_from_mongodb,
)


@pipeline
def generate_dataset(collection_name: str = "raw_data", limit: int = 500) -> None:
    fetch_from_mongodb(collection_name=collection_name, limit=limit)
