import asyncio
import json
import os

import psutil
from litellm import acompletion
from loguru import logger
from pydantic import BaseModel
from tqdm.asyncio import tqdm

from second_brain_offline import utils
from second_brain_offline.domain import Document


class QualityScoreResponseFormat(BaseModel):
    """Format for quality score responses from the language model.

    Attributes:
        score: A float between 0.0 and 1.0 representing the quality score.
    """

    score: float


class QualityScoreAgent:
    """Evaluates the quality of documents using LiteLLM with async support.

    This class handles the interaction with language models through LiteLLM to
    evaluate document quality based on relevance, factual accuracy, and information
    coherence. It supports both single and batch document processing.

    Attributes:
        model_id: The ID of the language model to use for quality evaluation.
        mock: If True, returns mock quality scores instead of using the model.
        max_concurrent_requests: Maximum number of concurrent API requests.
    """

    SYSTEM_PROMPT_TEMPLATE = """You are an expert judge tasked with evaluating the quality of a given DOCUMENT.

Guidelines:
1. Evaluate the DOCUMENT based on generally accepted facts and reliable information.
2. Evaluate that the DOCUMENT contains relevant information and not only links or error messages.
3. Check that the DOCUMENT doesn't oversimplify or generalize information in a way that changes its meaning or accuracy.

Analyze the text thoroughly and assign a quality score between 0 and 1, where:
- **0.0**: The DOCUMENT is completely irrelevant containing only noise such as links or error messages
- **0.1 - 0.7**: The DOCUMENT is partially relevant containing some relevant information checking partially guidelines
- **0.8 - 1.0**: The DOCUMENT is entirely relevant containing all relevant information following the guidelines

It is crucial that you return only the score in the following JSON format:
{{
    "score": <your score between 0.0 and 1.0>
}}

DOCUMENT:
{document}
"""

    def __init__(
        self,
        model_id: str = "gpt-4o-mini",
        mock: bool = False,
        max_concurrent_requests: int = 10,
    ) -> None:
        self.model_id = model_id
        self.mock = mock
        self.max_concurrent_requests = max_concurrent_requests

    def __call__(
        self, documents: Document | list[Document]
    ) -> Document | list[Document]:
        """Process single document or batch of documents for summarization.

        Args:
            documents: Single Document or list of Documents to summarize.

        Returns:
            Document | list[Document]: Processed document(s) with summaries.
        """

        is_single_document = isinstance(documents, Document)
        docs_list = [documents] if is_single_document else documents

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            results = asyncio.run(self.__get_quality_score_batch(docs_list))
        else:
            results = loop.run_until_complete(self.__get_quality_score_batch(docs_list))

        return results[0] if is_single_document else results

    async def __get_quality_score_batch(
        self, documents: list[Document]
    ) -> list[Document]:
        """Asynchronously score multiple documents with retry mechanism.

        Args:
            documents: List of documents to score.

        Returns:
            list[Document]: Documents with quality scores.
        """
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        total_docs = len(documents)
        logger.debug(
            f"Starting quality scoring batch with {self.max_concurrent_requests} concurrent requests. "
            f"Current process memory usage: {start_mem // (1024 * 1024)} MB"
        )

        scored_documents = await self.__process_batch(documents, await_time_seconds=7)
        documents_with_scores = [
            doc for doc in scored_documents if doc.content_quality_score is not None
        ]
        documents_without_scores = [
            doc for doc in scored_documents if doc.content_quality_score is None
        ]

        # Retry failed documents with increased await time, as most failures are due to rate limiting.
        if documents_without_scores:
            logger.info(
                f"Retrying {len(documents_without_scores)} failed documents with increased await time..."
            )
            retry_results = await self.__process_batch(
                documents_without_scores, await_time_seconds=20
            )

            documents_with_scores += retry_results

        end_mem = process.memory_info().rss
        memory_diff = end_mem - start_mem
        logger.debug(
            f"Quality scoring batch completed. "
            f"Final process memory usage: {end_mem // (1024 * 1024)} MB, "
            f"Memory diff: {memory_diff // (1024 * 1024)} MB"
        )

        success_count = len(
            [doc for doc in scored_documents if hasattr(doc, "quality_score")]
        )
        failed_count = total_docs - success_count
        logger.info(
            f"Quality scoring completed: "
            f"{success_count}/{total_docs} succeeded ✓ | "
            f"{failed_count}/{total_docs} failed ✗"
        )

        return scored_documents

    async def __process_batch(
        self, documents: list[Document], await_time_seconds: int
    ) -> list[Document]:
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        tasks = [
            self.__get_quality_score(
                document, semaphore, await_time_seconds=await_time_seconds
            )
            for document in documents
        ]
        results = []
        for coro in tqdm(
            asyncio.as_completed(tasks),
            total=len(documents),
            desc="Processing documents",
            unit="doc",
        ):
            result = await coro
            results.append(result)

        return results

    async def __get_quality_score(
        self,
        document: Document,
        semaphore: asyncio.Semaphore | None = None,
        await_time_seconds: int = 2,
    ) -> Document | None:
        """Generate a summary for a single document.

        Args:
            document: The Document object to summarize.
            semaphore: Optional semaphore for controlling concurrent requests.
            await_time_seconds: Time to wait for the model to respond.
        Returns:
            Document | None: Document with generated summary or None if failed.
        """
        if self.mock:
            return document.add_quality_score(score=0.5)

        async def process_document() -> Document:
            input_user_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
                document=document.content
            )
            try:
                input_user_prompt = utils.clip_tokens(
                    input_user_prompt, max_tokens=8192, model_id=self.model_id
                )
            except Exception as e:
                logger.warning(
                    f"Failed to clip tokens for document {document.id}: {str(e)}"
                )

            try:
                response = await acompletion(
                    model=self.model_id,
                    messages=[
                        {"role": "user", "content": input_user_prompt},
                    ],
                    stream=False,
                )
                await asyncio.sleep(await_time_seconds)  # Rate limiting

                if not response.choices:
                    logger.warning(
                        f"No quality score generated for document {document.id}"
                    )
                    return document

                raw_answer = response.choices[0].message.content
                quality_score = self._parse_model_output(raw_answer)
                if not quality_score:
                    logger.warning(
                        f"Failed to parse model output for document {document.id}"
                    )
                    return document

                return document.add_quality_score(
                    score=quality_score.score,
                )
            except Exception as e:
                logger.warning(f"Failed to score document {document.id}: {str(e)}")

                return document

        if semaphore:
            async with semaphore:
                return await process_document()

        return await process_document()

    def _parse_model_output(
        self, answer: str | None
    ) -> QualityScoreResponseFormat | None:
        if not answer:
            return None

        try:
            dict_content = json.loads(answer)
            return QualityScoreResponseFormat(
                score=dict_content["score"],
            )
        except Exception:
            return None


class HeuristicQualityAgent:
    """A rule-based agent for evaluating document quality based on simple heuristics.

    This agent evaluates document quality primarily by analyzing the ratio of URL content
    to total content length, assigning low scores to documents that are primarily
    composed of URLs.
    """

    def __call__(
        self, documents: Document | list[Document]
    ) -> Document | list[Document]:
        """Process single document or batch of documents for quality scoring.

        Args:
            documents: Single Document or list of Documents to evaluate.

        Returns:
            Document | list[Document]: Processed document(s) with quality scores.
        """
        is_single_document = isinstance(documents, Document)
        docs_list = [documents] if is_single_document else documents

        scored_documents = [self.__score_document(document) for document in docs_list]

        return scored_documents[0] if is_single_document else scored_documents

    def __score_document(self, document: Document) -> Document:
        """Score a single document based on URL content ratio.

        Calculates the ratio of URL content length to total content length.
        Documents with > 70% URL content receive a score of 0.0.

        Args:
            document: The Document object to score.

        Returns:
            Document: The input document with an added quality score.
        """

        if len(document.content) == 0:
            return document.add_quality_score(score=0.0)

        url_based_content = sum(len(url) for url in document.child_urls)
        url_content_ratio = url_based_content / len(document.content)

        if url_content_ratio >= 0.7:
            return document.add_quality_score(score=0.0)
        elif url_content_ratio >= 0.5:
            return document.add_quality_score(score=0.2)

        return document
