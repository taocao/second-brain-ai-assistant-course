from typing import Generator

from loguru import logger
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

    OPENAI_SUMMARY_SYSTEM_PROMPT = """You are a helpful assistant specialized in summarizing documents.
Your task is to create a clear, concise TL;DR summary in plain text.
Things to keep in mind while summarizing:
- titles of sections and sub-sections
- tags such as Generative AI, LLMs, etc.
- entities such as persons, organizations, processes, people, etc.
- the style such as the type, sentiment and writing style of the document
- the main findings and insights while preserving key information and main ideas
- ignore any irrelevant information such as cookie policies, privacy policies, HTTP errors,etc.

Document content:
{content}

Generate a concise summary of the key findings from the provided documents, highlighting the most significant insights and implications.
Return the document in plain text format regardless of the original format.
"""
    HUGGINGFACE_SUMMARY_SYSTEM_PROMPT = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
You are a helpful assistant specialized in summarizing documents. Generate a concise TL;DR summary in markdown format having a maximum of 512 characters of the key findings from the provided documents, highlighting the most significant insights

### Input:
{content}

### Response:
"""

    def __init__(self, stream: bool = False, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.__stream = stream
        self.__client, self.__system_prompt = self.__build_llm_client()

    def __build_llm_client(self) -> tuple[OpenAI, str]:
        if (
            settings.HUGGINGFACE_DEDICATED_ENDPOINT
            and settings.HUGGINGFACE_ACCESS_TOKEN
        ):
            logger.info(
                f"Found Hugging Face dedicated endpoint config. Using the following endpoint: {settings.HUGGINGFACE_DEDICATED_ENDPOINT}"
            )

            return OpenAI(
                base_url=settings.HUGGINGFACE_DEDICATED_ENDPOINT,
                api_key=settings.HUGGINGFACE_ACCESS_TOKEN,
            ), self.HUGGINGFACE_SUMMARY_SYSTEM_PROMPT
        else:
            logger.warning(
                "No Hugging Face dedicated endpoint config found. Default to using OpenAI as the summarizer."
            )

            return OpenAI(), self.OPENAI_SUMMARY_SYSTEM_PROMPT

    @track
    def forward(self, text: str) -> str | Generator[str, None, None]:
        result = self.__client.chat.completions.create(
            model="tgi",
            messages=[
                {
                    "role": "user",
                    "content": self.__system_prompt.format(content=text),
                },
            ],
            stream=self.__stream,
        )

        if self.__stream:
            for message in result:
                yield message.choices[0].delta.content
        else:
            return result.choices[0].message.content
