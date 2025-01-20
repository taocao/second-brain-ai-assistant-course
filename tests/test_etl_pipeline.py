import pytest
import yaml
from pathlib import Path
import logging
from second_brain.infrastructure.mongo.service import MongoDBService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.integration
class TestETLPipelineIntegration:
    @pytest.fixture(scope="class")
    def config(self):
        """Fixture to load ETL configuration"""
        config_path = Path("configs/etl.yaml")
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture(scope="class")
    def collection_name(self, config):
        """Fixture to get collection name from config"""
        return config['parameters']['load_collection_name']

    @pytest.fixture(scope="class")
    def mongodb_service(self, collection_name):
        """Fixture for MongoDB service connection"""
        with MongoDBService(collection_name=collection_name) as mongo_service:
            yield mongo_service

    def test_config_collection_name(self, collection_name):
        """Test the collection name in configuration"""
        assert collection_name == 'raw_data', "Unexpected collection name in config"

    def test_mongodb_connection(self, mongodb_service):
        """Test MongoDB connection and collection existence"""
        assert mongodb_service.collection is not None, "Failed to connect to MongoDB collection"

    def test_collection_has_documents(self, mongodb_service):
        """Test that the collection contains documents"""
        doc_count = mongodb_service.get_collection_count()
        assert doc_count > 0, "Collection is empty"

    def test_document_structure(self, mongodb_service):
        """Test the structure of documents in the collection"""
        sample_doc = mongodb_service.collection.find_one({})
        assert sample_doc is not None, "Failed to retrieve a document"

if __name__ == "__main__":
    pytest.main([__file__])
