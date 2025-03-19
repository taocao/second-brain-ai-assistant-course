import json
from typing import Any

from langchain_mongodb.retrievers.parent_document import (
    MongoDBAtlasParentDocumentRetriever,
)
from loguru import logger
from smolagents import LiteLLMModel, Tool, ToolCallingAgent

from rag_workshop.config import settings
from rag_workshop.retrievers import get_retriever


def build_agent() -> Any:
    """Builds and configures a tool-calling agent with MongoDB retriever capability.

    Returns:
        Any: A configured ToolCallingAgent instance with MongoDB retriever tool.
    """

    retriever_tool = MongoDBRetrieverTool()

    # TODO: Build model using LiteLLMModel
    model = ...

    # TODO: Build agent using ToolCallingAgent
    agent = ...

    return agent


class MongoDBRetrieverTool(Tool):
    """A tool for performing semantic search queries against a MongoDB vector database.

    This tool integrates with MongoDB Atlas to perform vector similarity search
    for document retrieval. It formats the results in XML-style markup for
    structured access to document metadata and content.

    Attributes:
        name (str): The identifier for this tool
        description (str): Detailed description of the tool's capabilities
        inputs (dict): Schema definition for the expected input parameters
        output_type (str): The type of data returned by this tool
    """

    ...
