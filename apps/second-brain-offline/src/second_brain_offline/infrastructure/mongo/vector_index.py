from loguru import logger
from pymongo.errors import OperationFailure
from pymongo.operations import SearchIndexModel

from second_brain_offline.infrastructure.mongo.service import MongoDBService


class MongoDBVectorIndex:
    def __init__(self, index_name: str, mongodb_client: MongoDBService) -> None:
        self.index_name = index_name
        self.mongodb_client = mongodb_client

    def create_vector_index(
        self, embedding_attribute_name: str, embedding_dim: int
    ) -> None:
        search_index_model = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": embedding_attribute_name,
                        "numDimensions": embedding_dim,
                        "similarity": "cosine",
                    }
                ]
            },
            name=self.index_name,
            type="vectorSearch",
        )

        try:
            self.mongodb_client.collection.create_search_index(model=search_index_model)
            logger.debug(
                f"Successfully created index {self.index_name} for collection {self.mongodb_client.collection_name}"
            )
        except OperationFailure:
            logger.error(
                f"Duplicate index {self.index_name} found for collection {self.mongodb_client.collection_name}. Skipping index creation."
            )
