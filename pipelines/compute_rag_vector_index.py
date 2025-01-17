from zenml import pipeline

from steps.compute_rag_vector_index import chunk_embed_load
from steps.infrastructure import (
    fetch_from_mongodb,
)


@pipeline
def compute_rag_vector_index(
    limit: int = 100,
    extract_collection_name: str = "raw_data",
    load_collection_name: str = "vector_index",
) -> None:
    documents = fetch_from_mongodb(limit=limit, collection_name=extract_collection_name)
    chunk_embed_load(documents, load_collection_name)
