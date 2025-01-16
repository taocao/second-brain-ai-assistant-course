import json
from pathlib import Path
from zenml.steps import step
from loguru import logger

from second_brain.infrastructure.mongo.service import MongoDBService


@step
def ingest_to_mongodb(
    mongodb_uri: str, 
    database_name: str, 
    collection_name: str, 
    data_directory: str
) -> None:
    """ZenML step to ingest JSON data from multiple files into MongoDB.

    Args:
        mongodb_uri (str): URI for MongoDB connection.
        database_name (str): Target database name.
        collection_name (str): Target collection name.
        data_directory (str): Path to the directory containing JSON files.

    Raises:
        Exception: If the ingestion process fails.
    """
    try:
        service = MongoDBService(mongodb_uri, database_name, collection_name)
        documents = read_all_json_files(data_directory)

        service.clear_collection()
        service.ingest_documents(documents)

        # Log total and genre-specific counts
        service.verify_collection_count()
    except Exception as e:
        logger.error(f"Failed to ingest documents: {e}")
        raise


def read_all_json_files(data_directory: str) -> list[dict]:
    """Reads all JSON files from a nested directory structure and combines them into a list.

    The function expects a directory structure of:
    data/database_id/page_id.json

    Args:
        data_directory (str): Path to the root data directory.

    Returns:
        List[Dict]: Combined list of dictionaries from all JSON files.

    Raises:
        FileNotFoundError: If the data directory doesn't exist.
        json.JSONDecodeError: If any JSON file is invalid.
    """
    all_documents: list[dict] = []
    data_path = Path(data_directory)

    if not data_path.exists():
        raise FileNotFoundError(f"Directory not found: {data_directory}")

    # Iterate through all database_id subdirectories
    for database_dir in data_path.iterdir():
        if database_dir.is_dir():
            # Find all .json files in the database directory
            json_files = database_dir.glob("*.json")
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        document = json.load(f)
                        all_documents.append(document)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON file {json_file}: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Error reading file {json_file}: {e}")
                    raise

    logger.info(f"Successfully read {len(all_documents)} JSON files")
    return all_documents
