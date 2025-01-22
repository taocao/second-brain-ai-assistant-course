import logging
from pathlib import Path

import pytest
import yaml

from second_brain_offline.config import settings
from second_brain_offline.entities.page import Page, PageMetadata
from second_brain_offline.infrastructure.mongo.service import MongoDBService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.integration
class TestDownloadRawDatasetIntegration:
    @pytest.fixture(scope="class")
    def config(self):
        """Fixture to load dataset configuration"""
        config_path = Path("configs/generate_dataset.yaml")
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    @pytest.fixture(scope="class")
    def mongodb_service(self):
        """Fixture for MongoDB service connection"""
        with MongoDBService(
            collection_name=settings.MONGODB_DATABASE_NAME
        ) as mongo_service:
            yield mongo_service

    @pytest.fixture(scope="class")
    def collection_name(self, config):
        """Fixture to get collection name from config"""
        return config["parameters"]["extract_collection_name"]

    def test_config_exists(self, config):
        """Test that the configuration file exists and is valid"""
        assert config is not None, "Failed to load configuration"
        assert "parameters" in config, "Configuration missing parameters section"

    def test_config_parameters(self, config):
        """Test the configuration parameters"""
        parameters = config["parameters"]
        assert "extract_collection_name" in parameters, (
            "Missing extract_collection_name parameter"
        )
        assert "limit" in parameters, "Missing limit parameter"
        assert isinstance(parameters["limit"], int), (
            "Limit parameter should be an integer"
        )

    def test_mongodb_connection(self, mongodb_service):
        """Test MongoDB connection"""
        assert mongodb_service.client is not None, "Failed to connect to MongoDB"
        assert mongodb_service.database is not None, "Failed to connect to database"

    def test_raw_collection_exists(self, mongodb_service, collection_name):
        """Test that the raw data collection exists"""
        collections = mongodb_service.database.list_collection_names()
        assert collection_name in collections, (
            f"Collection {collection_name} not found in database"
        )

    def test_raw_collection_has_documents(self, mongodb_service, collection_name):
        """Test that the raw collection contains documents"""
        collection = mongodb_service.database[collection_name]
        doc_count = collection.count_documents({})
        assert doc_count > 0, f"Collection {collection_name} is empty"

    def test_document_structure(self, mongodb_service, collection_name):
        """Test the structure of documents in the raw collection matches Page entity"""
        collection = mongodb_service.database[collection_name]
        sample_doc = collection.find_one({})
        assert sample_doc is not None, "Failed to retrieve a document"

        # Check required fields based on Page entity
        required_fields = ["metadata", "content", "urls"]
        for field in required_fields:
            assert field in sample_doc, f"Document missing required field: {field}"

        # Check metadata structure based on PageMetadata entity
        metadata = sample_doc["metadata"]
        assert isinstance(metadata, dict), "Metadata should be a dictionary"
        required_metadata_fields = ["id", "url", "title", "properties"]
        for field in required_metadata_fields:
            assert field in metadata, f"Metadata missing required field: {field}"

        # Validate types
        assert isinstance(sample_doc["content"], str), "Content should be string"
        assert isinstance(sample_doc["urls"], list), "URLs should be a list"
        assert isinstance(metadata["id"], str), "Metadata id should be string"
        assert isinstance(metadata["url"], str), "Metadata url should be string"
        assert isinstance(metadata["title"], str), "Metadata title should be string"
        assert isinstance(metadata["properties"], dict), (
            "Metadata properties should be dict"
        )

    def test_document_content_validity(self, mongodb_service, collection_name):
        """Test the content validity of documents"""
        collection = mongodb_service.database[collection_name]
        sample_doc = collection.find_one({})

        # Test if document can be converted to Page entity
        try:
            page = Page(
                metadata=PageMetadata(**sample_doc["metadata"]),
                content=sample_doc["content"],
                urls=sample_doc["urls"],
            )
            assert isinstance(page, Page), "Failed to create Page instance"
        except Exception as e:
            pytest.fail(f"Failed to create Page instance: {str(e)}")

        # Check content is not empty
        assert len(page.content.strip()) > 0, "Content should not be empty"

        # Check metadata fields are not empty
        assert len(page.metadata.id.strip()) > 0, "Metadata ID should not be empty"
        assert len(page.metadata.url.strip()) > 0, "Metadata URL should not be empty"
        assert len(page.metadata.title.strip()) > 0, (
            "Metadata title should not be empty"
        )

        # URLs can be empty list but must be a list
        assert isinstance(page.urls, list), "URLs must be a list"

    def test_document_serialization(self, mongodb_service, collection_name):
        """Test document can be serialized and deserialized"""
        collection = mongodb_service.database[collection_name]
        sample_doc = collection.find_one({})

        # Create Page instance
        page = Page(
            metadata=PageMetadata(**sample_doc["metadata"]),
            content=sample_doc["content"],
            urls=sample_doc["urls"],
        )

        # Test serialization
        try:
            serialized = page.model_dump_json()
            deserialized = Page.model_validate_json(serialized)
            assert isinstance(deserialized, Page), "Failed to deserialize Page"
        except Exception as e:
            pytest.fail(f"Serialization/deserialization failed: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__])
