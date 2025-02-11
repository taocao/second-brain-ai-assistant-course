"""
RAG (Retrieval Augmented Generation) implementation using LangChain.

This module provides functionality for question-answering using RAG with OpenAI models.
"""

import os
from pathlib import Path
from typing import Any, List

import click
import yaml
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


def load_retriever(config_path: Path) -> Any:
    """
    Load retriever configuration from YAML and initialize retriever.

    Args:
        retriever_type: Type of retriever to initialize.

    Returns:
        Any: Configured retriever instance.
    """

    config = yaml.safe_load(config_path.read_text())
    config = config["parameters"]

    print("--------LOADED CONFIG--------------")
    print(config)
    print("-----------------------------------")

    return get_retriever(
        embedding_model_id=config["embedding_model_id"],
        embedding_model_type=config["embedding_model_type"],
        retriever_type=config["retriever_type"],
        device=config["device"],
    )


def create_rag_chain(config_path: Path) -> Any:
    """
    Create and configure the RAG chain with retriever, prompt, and LLM.

    Returns:
        Any: Configured RAG chain ready for question answering.
    """
    retriever = load_retriever(config_path)

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
    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    parse_output = StrOutputParser()

    return retrieve | prompt | llm | parse_output


def get_documents_for_query(config_path: Path, query: str) -> List[str]:
    """
    Retrieve documents for a given query using the retriever.

    Args:
        query: The search query to retrieve documents for.

    Returns:
        List[str]: List of document contents matching the query.
    """

    retriever = load_retriever(config_path)
    documents = retriever.invoke(query)

    return [doc.page_content for doc in documents]


@click.command()
@click.option(
    "--config",
    "-c",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    help="Path to the RAG YAML configuration file",
)
def main(config_path: Path) -> None:
    """
    Main function to demonstrate RAG functionality.

    Args:
        config_path: Path to the YAML configuration file.
    """
    setup_environment()
    rag_chain = create_rag_chain(config_path)

    # Example queries
    questions = [
        "How can I optimize LLMs for inference?",
        "How is reinforcement learning applied to fine-tune LLMs?",
        "List some Python libraries to process and parse PDFs.",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        answer = rag_chain.invoke(question)
        print(f"Answer: {answer}")

    # Example document retrieval
    print(
        "\nRetrieving documents for 'List some Python libraries to process and parse PDFs':"
    )
    docs = get_documents_for_query(
        config_path, "List some Python libraries to process and parse PDFs"
    )
    for i, doc in enumerate(docs[:2]):
        print(f"\nDocument {i}:")
        print("-" * 100)
        print(doc)


if __name__ == "__main__":
    main()
