from typing import Dict, List

from bson import ObjectId
from loguru import logger
from pymongo import MongoClient, errors

from second_brain.config import settings


class MongoDBService:
    """Service class for MongoDB operations, supporting ingestion, querying, and validation.

    This class provides methods to interact with MongoDB collections, including document
    ingestion, querying, and validation operations.

    Attributes:
        client (MongoClient): MongoDB client instance for database connections.
        database (Database): Reference to the target MongoDB database.
        collection (Collection): Reference to the target MongoDB collection.
    """

    def __init__(
        self,
        collection_name: str,
        database_name: str = settings.MONGODB_DATABASE_NAME,
        mongodb_uri: str = settings.MONGODB_URI,
    ) -> None:
        """Initialize a connection to the MongoDB collection.

        Args:
            collection_name: Name of the MongoDB collection to use.
            database_name: Name of the MongoDB database to use.
                Defaults to value from settings.
            mongodb_uri: URI for connecting to MongoDB instance.
                Defaults to value from settings.

        Raises:
            Exception: If connection to MongoDB fails.
        """
        try:
            self.client = MongoClient(mongodb_uri)
            self.database = self.client[database_name]
            self.collection = self.database[collection_name]
            logger.info(
                f"Connected to MongoDB instance:\n URI: {mongodb_uri}\n Database: {database_name}\n Collection: {collection_name}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize MongoDBService: {e}")
            raise

    def clear_collection(self) -> None:
        """Remove all documents from the collection.

        This method deletes all documents in the collection to avoid duplicates
        during reingestion.

        Raises:
            errors.PyMongoError: If the deletion operation fails.
        """
        try:
            result = self.collection.delete_many({})
            logger.info(
                f"Cleared collection. Deleted {result.deleted_count} documents."
            )
        except errors.PyMongoError as e:
            logger.error(f"Error clearing the collection: {e}")
            raise

    def ingest_documents(self, documents: List[Dict]) -> None:
        """Insert multiple documents into the MongoDB collection.

        Args:
            documents: List of document dictionaries to insert.
                Each dictionary represents a single document.

        Raises:
            ValueError: If documents is empty or contains non-dictionary items.
            errors.PyMongoError: If the insertion operation fails.
        """
        try:
            if not documents or not all(isinstance(doc, dict) for doc in documents):
                raise ValueError("Documents must be a list of dictionaries.")

            # Remove '_id' fields to avoid duplicate key errors
            for doc in documents:
                doc.pop("_id", None)

            self.collection.insert_many(documents)
            logger.info(f"Inserted {len(documents)} documents into MongoDB.")
        except errors.PyMongoError as e:
            logger.error(f"Error inserting documents: {e}")
            raise

    def fetch_documents(self, limit: int, query: Dict) -> List[Dict]:
        """Retrieve documents from the MongoDB collection based on a query.

        Args:
            limit: Maximum number of documents to retrieve.
            query: MongoDB query filter to apply.

        Returns:
            List of documents matching the query, with ObjectIds converted to strings.

        Raises:
            Exception: If the query operation fails.
        """
        try:
            documents = list(self.collection.find(query).limit(limit))
            logger.info(f"Fetched {len(documents)} documents with query: {query}")
            return self.convert_objectid_to_str(documents)
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            raise

    @staticmethod
    def convert_objectid_to_str(documents: List[Dict]) -> List[Dict]:
        """Convert MongoDB ObjectId fields to string format.

        This method is used to prepare documents for JSON serialization by converting
        any ObjectId values to their string representation.

        Args:
            documents: List of MongoDB documents potentially containing ObjectId fields.

        Returns:
            Same documents with ObjectId fields converted to strings.
        """
        for doc in documents:
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
        return documents

    def verify_collection_count(self) -> int:
        """Count the total number of documents in the collection.

        Returns:
            Total number of documents in the collection.

        Raises:
            errors.PyMongoError: If the count operation fails.
        """
        try:
            count = self.collection.count_documents({})
            logger.info(f"Total documents in the collection: {count}")
            return count
        except errors.PyMongoError as e:
            logger.error(f"Error counting documents in MongoDB: {e}")
            raise

    def verify_genre(self, genre: str) -> int:
        """Count documents matching a specific genre using case-insensitive matching.

        Args:
            genre: Genre string to search for.

        Returns:
            Number of documents containing the specified genre.

        Raises:
            errors.PyMongoError: If the query operation fails.
        """
        query = {"genres": {"$regex": f"^{genre}$", "$options": "i"}}
        try:
            count = self.collection.count_documents(query)
            logger.info(f"Found {count} documents for genre '{genre}'.")
            return count
        except errors.PyMongoError as e:
            logger.error(f"Error verifying genre '{genre}': {e}")
            raise
