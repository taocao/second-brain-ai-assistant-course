"""
Module:
main.py

Purpose:
The main entry point for running the document ingestion and retrieval pipeline. It sets up configurations, runs the pipeline, and performs post-execution verifications.

Features:
- Validates input JSON data for document ingestion.
- Runs the ZenML pipeline to ingest and query MongoDB.
- Logs detailed execution details for validation and debugging.

Dependencies:
- MongoDBService for database operations.
- offline_pipeline for ZenML pipeline management.

Usage:
Execute this module directly to run the pipeline. Ensure all configurations are set in the `.env` file or `config.py`.
"""

import os

from loguru import logger

from pipelines.etl import etl
from second_brain.config import settings
from steps.infrastructure.fetch_from_mongodb import MongoDBService

def main():
    """
    Main function to execute the document ingestion and retrieval pipeline.

    Steps:
    1. Validate configurations and input JSON data.
    2. Run the ingestion and query pipeline.
    3. Perform post-execution verifications for document counts.

    Logs:
    - Total documents ingested.
    - Total documents matching the queried genre.

    Raises:
        Exception: If any error occurs during pipeline execution.
    """
    try:
        etl(
            ingest_json_config={
                "mongodb_uri": settings.MONGODB_OFFLINE_URI,
                "database_name": settings.MONGODB_OFFLINE_DATABASE,
                "collection_name": settings.MONGODB_OFFLINE_COLLECTION,
                "data_directory": settings.DATA_DIRECTORY,
            },
            fetch_documents_config={
                "mongodb_uri": settings.MONGODB_OFFLINE_URI,
                "database_name": settings.MONGODB_OFFLINE_DATABASE,
                "collection_name": settings.MONGODB_OFFLINE_COLLECTION,
                "limit": 100,
            },
        )

       
      
    except Exception as e:
        logger.error(f"An unexpected error occurred during pipeline execution: {e}")


if __name__ == "__main__":
    main()
