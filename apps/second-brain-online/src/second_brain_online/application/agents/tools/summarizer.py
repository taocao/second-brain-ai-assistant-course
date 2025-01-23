from typing import Generator

from openai import OpenAI
from opik import track
from smolagents import Tool

from second_brain_online.config import settings


class SummarizerTool(Tool):
    name = "summarizer"
    description = """Use this tool to summarize a piece of text. Especially useful when you need to summarize a document."""

    inputs = {
        "text": {
            "type": "string",
            "description": """The text to summarize.""",
        }
    }
    output_type = "string"

    def __init__(self, stream: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        assert settings.HUGGINGFACE_ACCESS_TOKEN, "HUGGINGFACE_ACCESS_TOKEN is not set"

        self.__stream = stream
        self.__client = OpenAI(
            base_url="https://psvenbzixv5z97fw.eu-west-1.aws.endpoints.huggingface.cloud/v1/",
            api_key=settings.HUGGINGFACE_ACCESS_TOKEN,
        )

    @track
    def forward(self, text: str) -> str | Generator[str, None, None]:
        result = self.__client.chat.completions.create(
            model="tgi",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides accurate and concise information.",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            stream=self.__stream,
        )

        if self.__stream:
            for message in result:
                yield message.choices[0].delta.content
        else:
            return result.choices[0].message.content
