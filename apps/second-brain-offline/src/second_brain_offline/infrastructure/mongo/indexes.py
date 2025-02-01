from langchain_mongodb.index import create_fulltext_search_index

from second_brain_offline.infrastructure.mongo.service import MongoDBService


class MongoDBHybridIndex:
    def __init__(
        self,
        retriever,
        mongodb_client: MongoDBService,
    ) -> None:
        self.retriever = retriever
        self.mongodb_client = mongodb_client

    def create(
        self,
        embedding_dim: int,
    ) -> None:
        vectorstore = self.retriever.vectorstore

        vectorstore.create_vector_search_index(
            dimensions=embedding_dim,
        )
        create_fulltext_search_index(
            collection=self.mongodb_client.collection,
            field=vectorstore._text_key,
            index_name=self.retriever.search_index_name,
        )
