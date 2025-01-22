from opik import track
from smolagents import Tool


class SummarizerTool(Tool):
    name = "summarizer"
    description = """Use this tool to summarize a query. Best used when you need to summarize a query, document or context."""

    inputs = {
        "text": {
            "type": "string",
            "description": """The text to summarize.""",
        }
    }
    output_type = "string"

    @track
    def forward(self, text: str) -> str:
        return "A summary of the query"
