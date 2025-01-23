from langchain_mongodb.retrievers import MongoDBAtlasParentDocumentRetriever

from second_brain_offline.config import settings

from .embeddings import get_embedding_model
from .splitters import get_splitter


def get_retriever(k: int = 3) -> MongoDBAtlasParentDocumentRetriever:
    embedding_model = get_embedding_model()
    retriever = MongoDBAtlasParentDocumentRetriever.from_connection_string(
        connection_string=settings.MONGODB_URI,
        embedding_model=embedding_model,
        child_splitter=get_splitter(200),
        parent_splitter=get_splitter(800),
        database_name=settings.MONGODB_DATABASE_NAME,
        collection_name="rag",
        text_key="page_content",
        search_kwargs={"k": k},
        allowed_special={"<|endoftext|>"},
    )

    return retriever
