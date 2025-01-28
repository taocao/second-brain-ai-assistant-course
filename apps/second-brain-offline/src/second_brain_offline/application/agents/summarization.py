import asyncio
import os

import psutil
from litellm import acompletion
from loguru import logger

from second_brain_offline.domain import Document


class SummarizationAgent:
    """Generates summaries for documents using LiteLLM with async support.

    This class handles the interaction with language models through LiteLLM to
    generate concise summaries while preserving key information from the original
    documents. It supports both single and batch document processing.

    Attributes:
        max_characters: Maximum number of characters for the summary.
        model_id: The ID of the language model to use for summarization.
        mock: If True, returns mock summaries instead of using the model.
        max_concurrent_requests: Maximum number of concurrent API requests.
    """

    SYSTEM_PROMPT = """You are a helpful assistant specialized in summarizing documents.
Your task is to create a clear, concise TL;DR summary in markdown format.
Things to keep in mind while summarizing:
- titles of sections and sub-sections should be kept
- tags such as Generative AI, LLMs, etc.
- entities such as persons, organizations, processes, people, etc.
- the style such as the type, sentiment and writing style of the document
- the main findings and insights while preserving key information and main ideas
- ignore any irrelevant information such as cookie policies, privacy policies, HTTP errors,etc.
"""

    USER_PROMPT_TEMPLATE = """Document content:
{content}

Generate a concise TL;DR summary having a maximum of 1000 characters of the key findings from the provided documents, highlighting the most significant insights and implications.
Return the document in markdown format regardless of the original format.
"""

    def __init__(
        self,
        max_characters: int,
        model_id: str = "gpt-4o-mini",
        mock: bool = False,
        max_concurrent_requests: int = 10,
    ) -> None:
        self.max_characters = max_characters
        self.model_id = model_id
        self.mock = mock
        self.max_concurrent_requests = max_concurrent_requests

    def __call__(
        self, documents: Document | list[Document], temperature: float = 0.0
    ) -> Document | list[Document]:
        """Process single document or batch of documents for summarization.

        Args:
            documents: Single Document or list of Documents to summarize.
            temperature: Temperature for the summarization model.
        Returns:
            Document | list[Document]: Processed document(s) with summaries.
        """

        is_single_document = isinstance(documents, Document)
        docs_list = [documents] if is_single_document else documents

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            results = asyncio.run(self.__summarize_batch(docs_list, temperature))
        else:
            results = loop.run_until_complete(
                self.__summarize_batch(docs_list, temperature)
            )

        return results[0] if is_single_document else results

    async def __summarize_batch(
        self, documents: list[Document], temperature: float = 0.0
    ) -> list[Document]:
        """Asynchronously summarize multiple documents.

        Args:
            documents: List of documents to summarize.
            temperature: Temperature for the summarization model.
        Returns:
            list[Document]: Documents with generated summaries.
        """

        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        logger.debug(
            f"Starting summarization batch with {self.max_concurrent_requests} concurrent requests. "
            f"Current process memory usage: {start_mem // (1024 * 1024)} MB"
        )

        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        tasks = [
            self.__summarize(document, semaphore, temperature) for document in documents
        ]
        results = await asyncio.gather(*tasks)

        end_mem = process.memory_info().rss
        memory_diff = end_mem - start_mem
        logger.debug(
            f"Summarization batch completed. "
            f"Final process memory usage: {end_mem // (1024 * 1024)} MB, "
            f"Memory diff: {memory_diff // (1024 * 1024)} MB"
        )

        successful_results = [result for result in results if result is not None]

        success_count = len(successful_results)
        failed_count = len(results) - success_count
        total_count = len(results)
        logger.info(
            f"Summarization completed: "
            f"{success_count}/{total_count} succeeded ✓ | "
            f"{failed_count}/{total_count} failed ✗"
        )

        return successful_results

    async def __summarize(
        self,
        document: Document,
        semaphore: asyncio.Semaphore | None = None,
        temperature: float = 0.0,
    ) -> Document | None:
        """Generate a summary for a single document.

        Args:
            document: The Document object to summarize.
            semaphore: Optional semaphore for controlling concurrent requests.
            temperature: Temperature for the summarization model.
        Returns:
            Document | None: Document with generated summary or None if failed.
        """
        if self.mock:
            return document.add_summary("This is a mock summary")

        async def process_document():
            user_prompt = self.USER_PROMPT_TEMPLATE.format(
                characters=self.max_characters, content=document.content
            )
            try:
                response = await acompletion(
                    model=self.model_id,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    stream=False,
                    temperature=temperature,
                )
                await asyncio.sleep(1)  # Rate limiting

                if not response.choices:
                    logger.warning(f"No summary generated for document {document.id}")
                    return None

                summary: str = response.choices[0].message.content
                return document.add_summary(summary)
            except Exception as e:
                logger.warning(f"Failed to summarize document {document.id}: {str(e)}")
                return None

        if semaphore:
            async with semaphore:
                return await process_document()

        return await process_document()
