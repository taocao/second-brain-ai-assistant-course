from langchain_mongodb.retrievers import MongoDBAtlasParentDocumentRetriever
from loguru import logger
from opik import track
from smolagents import Tool

from second_brain_online.application import rag
from second_brain_online.config import settings


class MongoDBRetrieverTool(Tool):
    name = "retriever"
    description = "Retrieve documents from MongoDB Atlas using semantic search."
    inputs = {"query": {"type": "string", "description": "User's query."}}
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.retriever = self.initialize_retriever()

    def initialize_retriever(self) -> MongoDBAtlasParentDocumentRetriever:
        """
        Initialize the MongoDB Atlas document retriever with embedding model.

        Returns:
            ParentDocumentRetriever: Configured retriever instance

        Note:
            This function sets up the document retriever with specific chunk sizes
            for both parent and child documents, optimizing for retrieval quality.
        """

        embedding_model = rag.EmbeddingModelBuilder().get_model()

        return MongoDBAtlasParentDocumentRetriever.from_connection_string(
            connection_string=settings.MONGODB_URI,
            embedding_model=embedding_model,
            child_splitter=rag.get_splitter(200),  # Smaller chunks for precise matching
            parent_splitter=rag.get_splitter(800),  # Larger chunks for context
            database_name=settings.MONGODB_DATABASE_NAME,
            collection_name="rag",
            text_key="page_content",
            search_kwargs={"k": 10},  # Number of documents to retrieve
        )

    @track
    def forward(self, query: str) -> str:
        try:
            raw_docs = self.retriever.invoke(query)
            return "\nRetrieved Documents:\n" + "\n\n".join(
                [
                    f"Document {i + 1}: {doc.page_content[:500]}..."
                    for i, doc in enumerate(raw_docs)
                ]
            )
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return "Error retrieving documents."
