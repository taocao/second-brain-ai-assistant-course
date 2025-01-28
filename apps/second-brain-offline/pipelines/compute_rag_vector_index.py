from zenml import pipeline

from steps.compute_rag_vector_index import chunk_embed_load
from steps.infrastructure import (
    fetch_from_mongodb,
)


@pipeline
def compute_rag_vector_index(
    extract_collection_name: str,
    load_collection_name: str,
    processing_batch_size: int = 256,
    processing_max_workers: int = 10,
    fetch_limit: int = 500,
) -> None:
    documents = fetch_from_mongodb(
        collection_name=extract_collection_name, limit=fetch_limit
    )
    chunk_embed_load(
        documents, load_collection_name, processing_batch_size, processing_max_workers
    )
