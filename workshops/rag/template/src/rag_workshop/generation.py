from typing import Any, List


def create_rag_chain() -> Any:
    """Creates and configures a RAG (Retrieval Augmented Generation) chain.

    The chain combines a retriever, prompt template, and language model to perform
    question answering over retrieved documents. It follows these steps:
    1. Retrieves relevant documents using the configured retriever
    2. Combines documents into context
    3. Processes the question with a prompt template
    4. Generates an answer using ChatGPT

    Returns:
        Any: A configured chain that takes a question string as input and returns
            an answer string based on retrieved context. Returns "I DON'T KNOW" if
            no relevant context is found.
    """

    # TODO: Implement RAG chain

    return rag_chain


def get_documents_for_query(query: str) -> List[str]:
    """Retrieves relevant documents for a given search query.

    Args:
        query: The search query to find matching documents.
            Should be a natural language question or keywords.

    Returns:
        List[str]: A list of document contents (as strings) that match the query,
            ordered by relevance. The number of results is limited by the
            RAG_TOP_K setting.
    """

    # TODO: Implement document retrieval logic
    ...

    return documents
