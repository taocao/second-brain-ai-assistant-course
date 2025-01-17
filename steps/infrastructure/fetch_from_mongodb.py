from loguru import logger
from zenml.steps import step

from second_brain.infrastructure.mongo import MongoDBService


@step
def fetch_from_mongodb(
    mongodb_uri: str, database_name: str, collection_name: str, limit: int
) -> list[dict]:
    """
    ZenML step to fetch MongoDB documents filtered by genre.

    Args:
        mongodb_uri (str): URI for MongoDB connection.
        database_name (str): Target database name.
        collection_name (str): Target collection name.
        limit (int): Maximum number of documents to fetch.
        genre (str): Genre to filter by.

    Returns:
        List[Dict]: Retrieved documents.

    Raises:
        Exception: If the fetch process fails.
    """

    try:
        service = MongoDBService(mongodb_uri, database_name, collection_name)

        # Fetch documents
        query = {}
        documents = service.fetch_documents(limit, query)

        # Log genre-specific counts
        # service.verify_genre(genre)

        return documents
    except Exception as e:
        logger.error(f"Failed to fetch documents: {e}")
        raise
