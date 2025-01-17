import asyncio
from typing import Generator

from langchain_core.documents import Document
from langchain_mongodb.retrievers import (
    MongoDBAtlasParentDocumentRetriever,
)
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.operations import SearchIndexModel
from zenml.steps import step

from second_brain.config import settings

BATCH_SIZE = 256
MAX_CONCURRENCY = 4


def get_splitter(chunk_size: int) -> RecursiveCharacterTextSplitter:
    """
    Returns a token-based text splitter with overlap
    Args:
        chunk_size (_type_): Chunk size in number of tokens
    Returns:
        RecursiveCharacterTextSplitter: Recursive text splitter object
    """
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=0.15 * chunk_size,
    )


embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")


@step
def chunk_embed_load(pages: list[dict], collection_name: str) -> None:
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

    mongodb_client = MongoClient(
        settings.MONGODB_URI, appname="devrel.showcase.parent_doc_retrieval"
    )
    mongodb_client.admin.command("ping")
    collection = mongodb_client[settings.MONGODB_DATABASE_NAME][collection_name]
    # Delete any existing documents from the collection
    collection.delete_many({})
    logger.info(
        f"Deleted {collection.count_documents({})} documents from {collection_name}"
    )

    docs = [
        Document(page_content=page["content"], metadata=page["metadata"])
        for page in pages
    ]
    asyncio.run(process_docs(parent_doc_retriever, docs[:10]))

    VS_INDEX_NAME = "vector_index"

    # Vector search index definition
    model = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": 1536,
                    "similarity": "cosine",
                }
            ]
        },
        name=VS_INDEX_NAME,
        type="vectorSearch",
    )

    # Check if the index already exists, if not create it
    try:
        collection.create_search_index(model=model)
        print(
            f"Successfully created index {VS_INDEX_NAME} for collection {collection_name}"
        )
    except OperationFailure:
        print(
            f"Duplicate index {VS_INDEX_NAME} found for collection {collection_name}. Skipping index creation."
        )


async def process_docs(
    parent_doc_retriever: MongoDBAtlasParentDocumentRetriever, docs: list[Document]
) -> list:
    """
    Asynchronously ingest LangChain documents into MongoDB
    Args:
        docs (List[Document]): List of LangChain documents
    Returns:
        List[None]: Results of the task executions
    """

    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    batches = get_batches(docs, BATCH_SIZE)
    tasks = []
    for batch in batches:
        tasks.append(process_batch(parent_doc_retriever, batch, semaphore))
    # Gather results from all tasks
    results = await asyncio.gather(*tasks)

    return results


def get_batches(docs: list[Document], batch_size: int) -> Generator:
    """
    Return batches of documents to ingest into MongoDB
    Args:
        docs (List[Document]): List of LangChain documents
        batch_size (int): Batch size
    Yields:
        Generator: Batch of documents
    """
    for i in range(0, len(docs), batch_size):
        yield docs[i : i + batch_size]


async def process_batch(
    parent_doc_retriever: MongoDBAtlasParentDocumentRetriever,
    batch: Generator,
    semaphore: asyncio.Semaphore,
) -> None:
    """
    Ingest batches of documents into MongoDB
    Args:
        batch (Generator): Chunk of documents to ingest
        semaphore (as): Asyncio semaphore
    """
    async with semaphore:
        await parent_doc_retriever.aadd_documents(batch)
        print(f"Processed {len(batch)} documents")
