from zenml import pipeline

from steps.etl import crawl, read_pages_from_disk
from steps.infrastructure import (
    ingest_to_mongodb,
)


@pipeline
def etl(data_directory: str, load_collection_name: str) -> None:
    pages = read_pages_from_disk(data_directory=data_directory)
    documents = crawl(pages=pages)
    ingest_to_mongodb(documents=documents, collection_name=load_collection_name)
