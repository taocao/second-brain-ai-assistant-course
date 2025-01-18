from loguru import logger
from zenml.steps import step

from second_brain.infrastructure.mongo.service import MongoDBService


@step
def ingest_to_mongodb(documents: list[dict], collection_name: str) -> None:
    """ZenML step to ingest documents into MongoDB.

    Args:
        documents (list[dict]): List of document dictionaries to ingest into MongoDB.

    Raises:
        Exception: If the ingestion process fails.
    """
    try:
        service = MongoDBService(collection_name=collection_name)

        service.clear_collection()
        service.ingest_documents(documents)

        service.get_collection_count()
    except Exception as e:
        logger.error(f"Failed to ingest documents: {e}")
        raise
