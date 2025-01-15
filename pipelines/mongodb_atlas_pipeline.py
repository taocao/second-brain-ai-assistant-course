"""
Module:
mongodb_atlas_pipeline.py

Purpose:
Defines the pipeline for document ingestion and retrieval using ZenML. This pipeline first ingests data from a JSON file into a MongoDB collection and then retrieves documents filtered by a specific genre.

Features:
- Modular pipeline design using ZenML.
- Sequential execution of ingestion and retrieval steps.
- Configuration-driven step parameters for flexible usage.

Dependencies:
- ZenML for pipeline orchestration.
- Custom steps for MongoDB ingestion and querying.

Usage:
This module defines the `offline_pipeline` that can be used to execute the defined steps. The parameters for each step must be provided during pipeline invocation.
"""

from zenml import pipeline
from steps.infrastructure.mongodb.mongodb_data_processing import (
    ingest_json_to_mongodb_step,
    fetch_documents_step,
)


@pipeline
def mongodb_atlas_pipeline(
    ingest_json_config: dict,
    fetch_documents_config: dict,
):
    """
    Defines the offline pipeline for MongoDB document ingestion and retrieval.

    Steps:
    1. `ingest_json_to_mongodb_step`: Reads data from a JSON file and inserts it into MongoDB.
    2. `fetch_documents_step`: Queries MongoDB for documents filtered by genre.

    Args:
        ingest_json_config (dict): Configuration for the ingestion step.
            Example:
                {
                    "mongodb_uri": "mongodb://mongodb-atlas-local:27017",
                    "database_name": "rag_pipeline",
                    "collection_name": "offline_documents",
                    "json_file_path": "./data/sample_data_set.json"
                }

        fetch_documents_config (dict): Configuration for the fetch step.
            Example:
                {
                    "mongodb_uri": "mongodb://mongodb-atlas-local:27017",
                    "database_name": "rag_pipeline",
                    "collection_name": "offline_documents",
                    "limit": 50,
                    "genre": "Western"
                }

    Execution Order:
    1. Data ingestion must be completed before querying to ensure that the collection contains up-to-date data.
    """
    # Step 1: Ingest JSON data into MongoDB
    ingest_json_to_mongodb_step(**ingest_json_config)

    # Step 2: Fetch documents from MongoDB based on the specified genre
    fetch_documents_step(**fetch_documents_config)
