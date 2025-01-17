from loguru import logger
from zenml.steps import step

from second_brain.infrastructure.mongo import MongoDBService


@step
def fetch_from_mongodb(limit: int, collection_name: str) -> list[dict]:
    try:
        service = MongoDBService(collection_name=collection_name)

        # Fetch documents
        query = {}
        documents = service.fetch_documents(limit, query)

        # Log genre-specific counts
        # service.verify_genre(genre)

        return documents
    except Exception as e:
        logger.error(f"Failed to fetch documents: {e}")
        raise
