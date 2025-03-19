import asyncio
import json
from pathlib import Path
from typing import Generator

from langchain_core.documents import Document
from loguru import logger
from tqdm.asyncio import tqdm

from rag_workshop.config import settings
from rag_workshop.mongodb import MongoDBService
from rag_workshop.retrievers import MongoDBAtlasParentDocumentRetriever


async def ingest_documents(
    documents_dir: Path,
    embedding_model_id: str,
    embedding_model_dim: int,
    device: str = "cpu",
) -> None:
    """Ingest documents from a directory into MongoDB with embeddings.

    Args:
        documents_dir: Directory containing JSON documents to process.
        embedding_model_id: ID of the embedding model to use.
        embedding_model_dim: Dimension of the embedding vectors.
        device: Device to run embeddings on ('cpu' or 'cuda'). Defaults to 'cpu'.
    """
    
    documents = extract_documents(documents_dir)

    filtered_documents = filter_documents(documents)

    await chunk_embed_load_documents(
        filtered_documents, embedding_model_id, embedding_model_dim, device
    )


def extract_documents(documents_dir: Path) -> list[Document]:
    """Load all JSON files from the specified directory into Document objects.

    Args:
        documents_dir (Path): Directory path containing JSON files to load.

    Returns:
        list[Document]: List of Document objects created from JSON files.
    """

    json_files = documents_dir.glob("*.json")
    documents = []
    for json_file in json_files:
        with json_file.open("r", encoding="utf-8") as f:
            document = json.load(f)

            metadata = document["metadata"]
            metadata["child_urls"] = document.get("child_urls", [])

            documents.append(
                Document(page_content=document["content"], metadata=metadata)
            )

    return documents


def filter_documents(documents: list[Document]) -> list[Document]:
    """Filter documents based on predefined criteria.

    Args:
        documents: List of documents to filter.

    Returns:
        List of filtered documents.
    """

    # TODO: Implement document filtering

    return documents


async def chunk_embed_load_documents(
    documents: list[Document],
    embedding_model_id: str,
    embedding_model_dim: int,
    device: str = "cpu",
) -> None:
    """Process documents by chunking, embedding, and loading into MongoDB.

    Args:
        documents: List of documents to process.
        embedding_model_id: Identifier for the embedding model.
        embedding_model_dim: Dimension of the embedding vectors.
        device: Device to run embeddings on ('cpu' or 'cuda'). Defaults to 'cpu'.
    """

    with MongoDBService(
        model=Document, collection_name=settings.MONGODB_RAG_COLLECTION_NAME
    ) as mongodb_client:
        mongodb_client.clear_collection()

        # TODO: Chunk, embed, and load documents into MongoDB
        ...

        # TODO: Create index
        ...


async def process_docs(
    retriever: MongoDBAtlasParentDocumentRetriever,
    docs: list[Document],
    batch_size: int = 4,
    max_concurrent: int = 2,
) -> None:
    """Process LangChain documents into MongoDB using async processing.

    Args:
        retriever: MongoDB Atlas document retriever instance.
        docs: List of LangChain documents to process.
        batch_size: Number of documents to process in each batch.
        max_concurrent: Maximum number of concurrent tasks.

    Returns:
        List[None]: List of None values representing completed batch processing results.
    """

    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [
        process_batch(retriever, batch, semaphore)
        for batch in get_batches(docs, batch_size)
    ]

    for coro in tqdm(
        asyncio.as_completed(tasks),
        total=len(docs) // batch_size + (1 if len(docs) % batch_size else 0),
        desc="Processing documents",
        unit="batch",
    ):
        await coro


def get_batches(
    docs: list[Document], batch_size: int
) -> Generator[list[Document], None, None]:
    """Return batches of documents to ingest into MongoDB.

    Args:
        docs: List of LangChain documents to batch.
        batch_size: Number of documents in each batch.

    Yields:
        Generator[list[Document]]: Batches of documents of size batch_size.
    """

    for i in range(0, len(docs), batch_size):
        yield docs[i : i + batch_size]


async def process_batch(
    retriever: MongoDBAtlasParentDocumentRetriever,
    documents_batch: list[Document],
    semaphore: asyncio.Semaphore,
) -> None:
    """Asynchronously ingest batches of documents into MongoDB.

    Args:
        retriever: MongoDB Atlas document retriever instance.
        documents_batch: List of documents to ingest in this batch.
        semaphore: Semaphore to control concurrent access.

    Raises:
        Exception: If there is an error processing the batch of documents.
    """

    async with semaphore:
        try:
            # TODO: Ingest documents into MongoDB
            logger.info(f"Successfully processed {len(documents_batch)} documents.")
        except Exception as e:
            logger.warning(
                f"Error processing batch of {len(documents_batch)} documents: {str(e)}"
            )
