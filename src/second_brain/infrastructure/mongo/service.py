from typing import List, Dict
from pymongo import MongoClient, errors
from bson import ObjectId
from loguru import logger


class MongoDBService:
    """
    Service class for MongoDB operations, supporting ingestion, querying, and validation.

    Attributes:
        client (MongoClient): MongoDB client instance for database interaction.
        database (Database): Reference to the target database.
        collection (Collection): Reference to the target collection.
    """

    def __init__(self, mongodb_uri: str, database_name: str, collection_name: str):
        """
        Initialize a connection to the MongoDB collection.

        Args:
            mongodb_uri (str): URI for connecting to MongoDB.
            database_name (str): Target database name.
            collection_name (str): Target collection name.

        Raises:
            Exception: If the connection to MongoDB fails.
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

    def clear_collection(self):
        """
        Remove all documents from the collection to avoid duplicates.

        Raises:
            PyMongoError: If the operation fails.
        """
        try:
            result = self.collection.delete_many({})
            logger.info(
                f"Cleared collection. Deleted {result.deleted_count} documents."
            )
        except errors.PyMongoError as e:
            logger.error(f"Error clearing the collection: {e}")
            raise

    def ingest_documents(self, documents: List[Dict]):
        """
        Insert a list of documents into the MongoDB collection.

        Args:
            documents (List[Dict]): List of dictionaries to be inserted.

        Raises:
            ValueError: If the input is invalid.
            PyMongoError: If the insertion operation fails.
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
        """
        Retrieve documents from the MongoDB collection based on a query.

        Args:
            limit (int): Maximum number of documents to retrieve.
            query (Dict): Query filter for MongoDB.

        Returns:
            List[Dict]: List of retrieved documents.

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
        """
        Convert MongoDB ObjectId fields to string format for serialization.

        Args:
            documents (List[Dict]): List of MongoDB documents.

        Returns:
            List[Dict]: Documents with ObjectId fields converted to strings.
        """
        for doc in documents:
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
        return documents

    def verify_collection_count(self) -> int:
        """
        Count the total number of documents in the collection.

        Returns:
            int: Total document count.

        Raises:
            PyMongoError: If the count operation fails.
        """
        try:
            count = self.collection.count_documents({})
            logger.info(f"Total documents in the collection: {count}")
            return count
        except errors.PyMongoError as e:
            logger.error(f"Error counting documents in MongoDB: {e}")
            raise

    def verify_genre(self, genre: str) -> int:
        """
        Count the number of documents matching a specific genre.

        Args:
            genre (str): Genre to filter by.

        Returns:
            int: Count of documents matching the genre.

        Raises:
            PyMongoError: If the query operation fails.
        """
        query = {"genres": {"$regex": f"^{genre}$", "$options": "i"}}
        try:
            count = self.collection.count_documents(query)
            logger.info(f"Found {count} documents for genre '{genre}'.")
            return count
        except errors.PyMongoError as e:
            logger.error(f"Error verifying genre '{genre}': {e}")
            raise