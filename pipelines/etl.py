from zenml import pipeline
from steps.infrastructure import (
    ingest_to_mongodb,
    fetch_from_mongodb,
)

from second_brain.config import settings

@pipeline
def etl() -> None:
    ingest_json_config= {
                "mongodb_uri": settings.MONGODB_OFFLINE_URI,
                "database_name": settings.MONGODB_OFFLINE_DATABASE,
                "collection_name": settings.MONGODB_OFFLINE_COLLECTION,
                "data_directory": settings.DATA_DIRECTORY,
            }
    fetch_documents_config = {
        "mongodb_uri": settings.MONGODB_OFFLINE_URI,
        "database_name": settings.MONGODB_OFFLINE_DATABASE,
        "collection_name": settings.MONGODB_OFFLINE_COLLECTION,
        "limit": 100,
    }
    
    ingest_to_mongodb(**ingest_json_config)

    fetch_from_mongodb(**fetch_documents_config)
