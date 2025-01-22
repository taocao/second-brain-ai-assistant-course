from loguru import logger
from opik import track
from smolagents import Tool

from second_brain_online.application.rag import get_retriever


class MongoDBRetrieverTool(Tool):
    name = "mongodb_vector_search_retriever"
    description = """Use this tool to search and retrieve relevant documents from a knowledge base using semantic search.
    This tool performs similarity-based search to find the most relevant documents matching the query.
    Best used when you need to:
    - Find specific information from stored documents
    - Get context about a topic
    - Research historical data or documentation
    The tool will return multiple relevant document snippets."""

    inputs = {
        "query": {
            "type": "string",
            "description": """The search query to find relevant documents for using semantic search.
            Should be a clear, specific question or statement about the information you're looking for.""",
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.retriever = get_retriever()

    @track
    def forward(self, query: str) -> str:
        try:
            raw_docs = self.retriever.invoke(query)

            formatted_docs = []
            for i, doc in enumerate(raw_docs, 1):
                formatted_docs.append(
                    f"""
<document id="{i}">
{doc.page_content.strip()}
</document>"""
                )

            return "\n".join(["<search_results>", *formatted_docs, "</search_results>"])
        except Exception:
            logger.opt(exception=True).debug("Error retrieving documents.")

            return "Error retrieving documents."
