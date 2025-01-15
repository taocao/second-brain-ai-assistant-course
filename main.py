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
import json
import logging
from steps.infrastructure.mongodb.mongodb_data_processing import MongoDBService
from zenml.logger import get_logger
from pipelines.mongodb_atlas_pipeline import mongodb_atlas_pipeline
from src.second_brain.config import Settings

# TODO: Replace all current logger configurations with loguru.
# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# TODO: Replace all current logger configurations with loguru.
# Flag to enable/disable structured logging
ENABLE_STRUCTURED_LOGGING = (
    os.getenv("ENABLE_STRUCTURED_LOGGING", "false").lower() == "true"
)


# TODO: Replace all current logger configurations with loguru.
def log_section(title: str, content: str = "", level=logging.INFO):
    """
    Log a structured section with a title and optional content,
    based on the structured logging flag.

    Args:
        title (str): Title of the section.
        content (str): Optional content to log.
        level (int): Log level (default is INFO).
    """
    if ENABLE_STRUCTURED_LOGGING:
        # logger.log(level, "\n" + "=" * 60)
        logger.log(level, "=" * 60)
        logger.log(level, f"{title}")
        if content:
            logger.log(level, "-" * 60)
            logger.log(level, content)
        logger.log(level, "=" * 60)
        # logger.log(level, "=" * 60 + "\n")
    else:
        # Default logging behavior
        logger.log(level, f"{title}: {content}")


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
        # Load settings
        settings = Settings()
        genre = settings.DEFAULT_GENRE  # Use environment-defined genre

        # Validate input JSON
        with open(settings.LOCAL_JSON_FILE_PATH, "r") as file:
            documents = json.load(file)
        expected_genre_count = sum(
            1 for doc in documents if "genres" in doc and genre in doc["genres"]
        )
        log_section(
            f"Expected '{genre}' genre count in JSON file: {expected_genre_count}"
        )

        # Run the pipeline
        mongodb_pipeline_instance = mongodb_atlas_pipeline(
            ingest_json_config={
                "mongodb_uri": settings.MONGODB_OFFLINE_URI,
                "database_name": settings.MONGODB_OFFLINE_DATABASE,
                "collection_name": settings.MONGODB_OFFLINE_COLLECTION,
                "json_file_path": settings.LOCAL_JSON_FILE_PATH,
            },
            fetch_documents_config={
                "mongodb_uri": settings.MONGODB_OFFLINE_URI,
                "database_name": settings.MONGODB_OFFLINE_DATABASE,
                "collection_name": settings.MONGODB_OFFLINE_COLLECTION,
                "limit": settings.MAX_FETCH_LIMIT,
                "genre": genre,
            },
        )

        # Post-run validation
        service = MongoDBService(
            settings.MONGODB_OFFLINE_URI,
            settings.MONGODB_OFFLINE_DATABASE,
            settings.MONGODB_OFFLINE_COLLECTION,
        )
        log_section("Verifying document ingestion and genre query...")
        total_documents = service.verify_collection_count()
        genre_count = service.verify_genre(genre)

        # Log results
        log_section(f"Total documents in the collection: {total_documents}")
        log_section(f"Total documents found for genre '{genre}': {genre_count}")
        log_section("\nPipeline execution completed.")
        log_section(f"Pipeline run details:")
        log_section(f"  ID: {mongodb_pipeline_instance.id}")
        log_section(f"  Name: {mongodb_pipeline_instance.name}")
        log_section(f"  Status: {mongodb_pipeline_instance.status}")
        log_section(f"  Created: {mongodb_pipeline_instance.created}")
        log_section(f"  Ended: {mongodb_pipeline_instance.end_time}")

    except Exception as e:
        logger.error(f"An unexpected error occurred during pipeline execution: {e}")


if __name__ == "__main__":
    os.makedirs("./logs", exist_ok=True)
    log_section("Log directory created or already exists.")
    main()
