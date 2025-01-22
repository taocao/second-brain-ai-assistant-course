from zenml.steps import step

from second_brain_offline.infrastructure.mongo import MongoDBService


@step
def fetch_from_mongodb(limit: int, collection_name: str) -> list[dict]:
    with MongoDBService(collection_name=collection_name) as service:
        documents = service.fetch_documents(limit, query={})

    return documents
