from zenml import pipeline

from second_brain_offline.application.rag import EmbeddingModelType
from steps.compute_rag_vector_index import chunk_embed_load, filter_by_quality
from steps.infrastructure import (
    fetch_from_mongodb,
)


@pipeline
def compute_rag_vector_index(
    extract_collection_name: str,
    fetch_limit: int,
    load_collection_name: str,
    content_quality_score_threshold: float,
    embedding_model_id: str,
    embedding_model_type: EmbeddingModelType,
    embedding_model_dim: int,
    chunk_size: int,
    contextual_agent_model_id: str,
    contextual_agent_max_characters: int,
    mock: bool,
    processing_batch_size: int = 256,
    processing_max_workers: int = 10,
    device: str = "cpu",
) -> None:
    documents = fetch_from_mongodb(
        collection_name=extract_collection_name, limit=fetch_limit
    )
    documents = filter_by_quality(
        documents=documents,
        content_quality_score_threshold=content_quality_score_threshold,
    )
    chunk_embed_load(
        documents=documents,
        collection_name=load_collection_name,
        processing_batch_size=processing_batch_size,
        processing_max_workers=processing_max_workers,
        embedding_model_id=embedding_model_id,
        embedding_model_type=embedding_model_type,
        embedding_model_dim=embedding_model_dim,
        chunk_size=chunk_size,
        contextual_agent_model_id=contextual_agent_model_id,
        contextual_agent_max_characters=contextual_agent_max_characters,
        mock=mock,
        device=device,
    )
