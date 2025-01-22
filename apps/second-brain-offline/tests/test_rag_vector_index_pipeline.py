import os

import pytest
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_mongodb.retrievers import MongoDBAtlasParentDocumentRetriever
from langchain_openai import ChatOpenAI

from second_brain_offline.application.rag import get_splitter
from second_brain_offline.application.rag.embeddings import EmbeddingModelBuilder
from second_brain_offline.config import settings
from second_brain_offline.infrastructure.mongo import MongoDBService


@pytest.mark.integration
class TestRAGChainIntegration:
    @pytest.fixture(scope="class")
    def mongodb_client(self):
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        return MongoDBService(settings.MONGODB_URI)

    @pytest.fixture(scope="class")
    def parent_doc_retriever(self):
        embedding_model = EmbeddingModelBuilder().get_model()
        return MongoDBAtlasParentDocumentRetriever.from_connection_string(
            connection_string=settings.MONGODB_URI,
            embedding_model=embedding_model,
            child_splitter=get_splitter(200),
            parent_splitter=get_splitter(800),
            database_name=settings.MONGODB_DATABASE_NAME,
            collection_name="rag_data",
            text_key="page_content",
            search_kwargs={"k": 10},
        )

    @pytest.fixture(scope="class")
    def rag_chain(self, parent_doc_retriever):
        # Retrieve and parse documents
        retrieve = {
            "context": parent_doc_retriever
            | (lambda docs: "\n\n".join([d.page_content for d in docs])),
            "question": RunnablePassthrough(),
        }

        template = """Answer the question based only on the following context. If no context is provided, respond with I DON'T KNOW: \
{context}

Question: {question}
"""
        # Define the chat prompt
        prompt = ChatPromptTemplate.from_template(template)
        # Define the model to be used for chat completion
        llm = ChatOpenAI(temperature=0, model="gpt-4o-2024-11-20")
        # Parse output as a string
        parse_output = StrOutputParser()
        # Naive RAG chain
        return retrieve | prompt | llm | parse_output

    @pytest.mark.skipif(
        not settings.OPENAI_API_KEY, reason="OpenAI API key not available"
    )
    def test_rag_chain_real_inference(self, rag_chain):
        """
        This test performs a real query against the vector database and runs actual inference.
        Uses the same question as in the notebook for consistency.
        """
        # Test with the exact question from the notebook
        test_question = "How can I optimize LLMs for inference?"
        response = rag_chain.invoke(test_question)

        # Assertions
        assert isinstance(response, str)
        assert len(response) > 0
        assert response != "I DON'T KNOW"

        # Check for expected optimization techniques mentioned in the notebook
        expected_topics = [
            "quantization",
            "GGUF",
            "GPTQ",
            "EXL2",
            "AWQ",
            "CPU optimization",
            "GPU optimization",
        ]

        # At least some of these topics should be present in the response
        matches = sum(
            1 for topic in expected_topics if topic.lower() in response.lower()
        )
        assert matches > 0, (
            "Response should contain at least one known optimization technique"
        )

        # Log the actual response for manual review
        print(f"\nQuestion: {test_question}")
        print(f"Response: {response}")

    @pytest.mark.skipif(
        not settings.OPENAI_API_KEY, reason="OpenAI API key not available"
    )
    def test_rag_chain_unknown_topic(self, rag_chain):
        """
        Test with a question that should not be in your knowledge base
        """
        test_question = "What is the current weather in Paris?"
        response = rag_chain.invoke(test_question)

        assert "I DON'T KNOW" in response.upper()
