from zenml import pipeline

from steps.infrastructure import (
    fetch_from_mongodb,
)


@pipeline
def compute_rag_vector_index(limit: int = 100, extract_collection_name: str = "raw_data") -> None:
    fetch_from_mongodb(limit=limit, collection_name=extract_collection_name)
