from zenml import pipeline

from second_brain.config import settings
from steps.infrastructure import (
    fetch_from_mongodb,
)


@pipeline
def compute_rag_vector_index() -> None:
    fetch_documents_config = {
        "mongodb_uri": settings.MONGODB_OFFLINE_URI,
        "database_name": settings.MONGODB_OFFLINE_DATABASE,
        "collection_name": settings.MONGODB_OFFLINE_COLLECTION,
        "limit": 100,
    }

    fetch_from_mongodb(**fetch_documents_config)
