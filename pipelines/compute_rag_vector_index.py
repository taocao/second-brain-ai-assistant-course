from zenml import pipeline

from steps.compute_rag_vector_index import chunk_embed_load
from steps.infrastructure import (
    fetch_from_mongodb,
)


@pipeline
def compute_rag_vector_index(
    extract_collection_name: str = "raw_data",
    load_collection_name: str = "vector_index",
    processing_batch_size: int = 256,
    processing_max_workers: int = 10,
    fetch_limit: int = 100,
) -> None:
    documents = fetch_from_mongodb(limit=fetch_limit, collection_name=extract_collection_name)
    chunk_embed_load(documents, load_collection_name, processing_batch_size, processing_max_workers)
