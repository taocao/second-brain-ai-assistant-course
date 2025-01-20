from loguru import logger
from pydantic import BaseModel
from zenml.steps import step

from second_brain.infrastructure.mongo.service import MongoDBService


@step
def ingest_to_mongodb(documents: list[BaseModel], collection_name: str) -> None:
    """ZenML step to ingest documents into MongoDB.

    Args:
        documents (list[dict]): List of document dictionaries to ingest into MongoDB.

    Raises:
        Exception: If the ingestion process fails.
    """

    with MongoDBService(collection_name=collection_name) as service:
        service.clear_collection()
        service.ingest_documents(documents)

        count = service.get_collection_count()
        logger.info(
            f"Successfully ingested {count} documents into MongoDB collection '{collection_name}'"
        )
