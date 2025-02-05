"""
RAG (Retrieval Augmented Generation) implementation using LangChain.

This module provides functionality for question-answering using RAG with OpenAI models.
"""

import os
from typing import Any, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from second_brain_offline.application.rag import get_retriever
from second_brain_offline.config import settings


def setup_environment() -> None:
    """
    Set up the environment variables needed for the application.
    """
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY


def create_rag_chain() -> Any:
    """
    Create and configure the RAG chain with retriever, prompt, and LLM.

    Returns:
        Any: Configured RAG chain ready for question answering.
    """
    retriever = get_retriever(embedding_model_id="text-embedding-3-small")

    # Retrieve and parse documents
    retrieve = {
        "context": retriever
        | (lambda docs: "\n\n".join([d.page_content for d in docs])),
        "question": RunnablePassthrough(),
    }

    template = """Answer the question based only on the following context. If no context is provided, respond with I DON'T KNOW: \
{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(temperature=0, model="gpt-4-0125-preview")
    parse_output = StrOutputParser()

    return retrieve | prompt | llm | parse_output


def get_documents_for_query(query: str) -> List[str]:
    """
    Retrieve documents for a given query using the retriever.

    Args:
        query: The search query to retrieve documents for.

    Returns:
        List[str]: List of document contents matching the query.
    """
    retriever = get_retriever(embedding_model_id="text-embedding-3-small")
    documents = retriever.invoke(query)
    return [doc.page_content for doc in documents]


def main() -> None:
    """
    Main function to demonstrate RAG functionality.
    """
    setup_environment()
    rag_chain = create_rag_chain()

    # Example queries
    questions = [
        "How can I optimize LLMs for inference?",
        "What is RAGAS?",
        "How does Tensorflow Recommenders work?",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        answer = rag_chain.invoke(question)
        print(f"Answer: {answer}")

    # Example document retrieval
    print("\nRetrieving documents for 'Evaluating RAG Applications with RAGAs':")
    docs = get_documents_for_query("Evaluating RAG Applications with RAGAs")
    for i, doc in enumerate(docs):
        print(f"\nDocument {i}:")
        print("-" * 100)
        print(doc)


if __name__ == "__main__":
    main()
