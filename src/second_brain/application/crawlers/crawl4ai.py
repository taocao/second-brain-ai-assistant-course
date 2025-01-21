import asyncio
import os

import psutil
from crawl4ai import AsyncWebCrawler, CacheMode
from loguru import logger

from second_brain import utils
from second_brain.domain import Document, DocumentMetadata


class Crawl4AICrawler:
    """A crawler implementation using crawl4ai library for concurrent web crawling.

    Attributes:
        max_concurrent_requests: Maximum number of concurrent HTTP requests allowed.
    """

    def __init__(self, max_concurrent_requests: int = 10) -> None:
        """Initialize the crawler.

        Args:
            max_concurrent_requests: Maximum number of concurrent requests. Defaults to 10.
        """
        self.max_concurrent_requests = max_concurrent_requests

    def __call__(self, page: Document) -> list[Document]:
        """Crawl a document's child URLs.

        Args:
            page: Document containing child URLs to crawl.

        Returns:
            list[Document]: List of new documents created from crawled child URLs.
        """
        content = asyncio.run(self.__crawl(page))
        return content

    async def __crawl(self, page: Document) -> list[Document]:
        """Asynchronously crawl all child URLs of a document.

        Args:
            page: Document containing child URLs to crawl.

        Returns:
            list[Document]: List of new documents created from successfully crawled URLs.
        """
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        logger.debug(
            f"Starting crawl batch with {self.max_concurrent_requests} concurrent requests. "
            f"Current process memory usage: {start_mem // (1024 * 1024)} MB"
        )

        semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        async with AsyncWebCrawler(cache_mode=CacheMode.BYPASS) as crawler:
            tasks = [
                self.__crawl_url(crawler, page, url, semaphore)
                for url in page.child_urls
            ]
            results = await asyncio.gather(*tasks)

        end_mem = process.memory_info().rss
        crawling_memory_diff = end_mem - start_mem
        logger.debug(
            f"Crawl batch completed. "
            f"Final process memory usage: {end_mem // (1024 * 1024)} MB, "
            f"Crawling memory usage: {crawling_memory_diff // (1024 * 1024)} MB"
        )

        successful_results = [result for result in results if result is not None]

        success_count = len(successful_results)
        failed_count = len(results) - success_count
        total_count = len(results)
        logger.info(
            f"Crawling completed: "
            f"{success_count}/{total_count} succeeded ✓ | "
            f"{failed_count}/{total_count} failed ✗"
        )

        results = [result for result in results if result is not None]

        return results

    async def __crawl_url(
        self,
        crawler: AsyncWebCrawler,
        page: Document,
        url: str,
        semaphore: asyncio.Semaphore,
    ) -> Document | None:
        """Crawl a single URL and create a new document.

        Args:
            crawler: AsyncWebCrawler instance to use for crawling.
            page: Parent document containing the URL.
            url: URL to crawl.
            semaphore: Semaphore for controlling concurrent requests.

        Returns:
            Document | None: New document if crawl was successful, None otherwise.
        """

        async with semaphore:
            result = await crawler.arun(url=url)

            if not result or not result.success:
                logger.warning(f"Failed to crawl {url}")
                return None

            if result.markdown is None:
                logger.warning(f"Failed to crawl {url}")
                return None

            child_links = [
                link["href"]
                for link in result.links["internal"] + result.links["external"]
            ]
            if result.metadata:
                title = result.metadata.pop("title", "") or ""
            else:
                title = ""

            document_id = utils.generate_random_hex(length=32)

            return Document(
                id=document_id,
                metadata=DocumentMetadata(
                    id=document_id,
                    url=url,
                    title=title,
                    properties=result.metadata or {},
                ),
                parent_metadata=page.metadata,
                content=str(result.markdown),
                child_urls=child_links,
            )
