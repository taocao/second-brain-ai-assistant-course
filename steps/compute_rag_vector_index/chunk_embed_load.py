from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Generator

from langchain_core.documents import Document as LangChainDocument
from langchain_mongodb.retrievers import (
    MongoDBAtlasParentDocumentRetriever,
)
from tqdm import tqdm
from zenml.steps import step

from second_brain.application.rag import get_splitter
from second_brain.application.rag.embeddings import EmbeddingModelBuilder
from second_brain.config import settings
from second_brain.domain import Document
from second_brain.infrastructure.mongo import MongoDBService, MongoDBVectorIndex


@step
def chunk_embed_load(
    pages: list[Document],
    collection_name: str,
    processing_batch_size: int,
    processing_max_workers: int,
) -> None:
    embedding_model = EmbeddingModelBuilder().get_model()
    parent_doc_retriever = MongoDBAtlasParentDocumentRetriever.from_connection_string(
        connection_string=settings.MONGODB_URI,
        embedding_model=embedding_model,
        child_splitter=get_splitter(200),
        parent_splitter=get_splitter(800),
        database_name=settings.MONGODB_DATABASE_NAME,
        collection_name=collection_name,
        text_key="page_content",
        search_kwargs={"k": 10},
    )

    with MongoDBService(
        model=Document, collection_name=collection_name
    ) as mongodb_client:
        mongodb_client.clear_collection()

        docs = [
            LangChainDocument(page_content=page.content, metadata=page.metadata.model_dump())
            for page in pages
        ]
        process_docs(
            parent_doc_retriever,
            docs,
            batch_size=processing_batch_size,
            max_workers=processing_max_workers,
        )

        vector_index = MongoDBVectorIndex(
            index_name="vector_index", mongodb_client=mongodb_client
        )
        vector_index.create_vector_index(
            embedding_attribute_name="embedding", embedding_dim=1536
        )


def process_docs(
    parent_doc_retriever: MongoDBAtlasParentDocumentRetriever,
    docs: list[LangChainDocument],
    batch_size: int = 256,
    max_workers: int = 2,
) -> list[None]:
    """Process LangChain documents into MongoDB using thread pool.

    Args:
        parent_doc_retriever: MongoDB Atlas document retriever instance.
        docs: List of LangChain documents to process.
        batch_size: Number of documents to process in each batch. Defaults to 256.
        max_workers: Maximum number of concurrent threads. Defaults to 10.

    Returns:
        List of None values representing completed batch processing results.
    """
    batches = list(get_batches(docs, batch_size))
    results = []
    total_docs = len(docs)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_batch, parent_doc_retriever, batch)
            for batch in batches
        ]

        with tqdm(total=total_docs, desc="Processing documents") as pbar:
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                pbar.update(batch_size)

    return results


def get_batches(
    docs: list[LangChainDocument], batch_size: int
) -> Generator[list[LangChainDocument], None, None]:
    """Return batches of documents to ingest into MongoDB.

    Args:
        docs: List of LangChain documents to batch.
        batch_size: Number of documents in each batch.

    Yields:
        Batches of documents of size batch_size.
    """
    for i in range(0, len(docs), batch_size):
        yield docs[i : i + batch_size]


def process_batch(
    parent_doc_retriever: MongoDBAtlasParentDocumentRetriever,
    batch: list[LangChainDocument],
) -> None:
    """Ingest batches of documents into MongoDB.

    Args:
        parent_doc_retriever: MongoDB Atlas document retriever instance.
        batch: List of documents to ingest in this batch.
    """

    parent_doc_retriever.add_documents(batch)
    print(f"Processed {len(batch)} documents")
