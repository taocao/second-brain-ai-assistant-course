import asyncio

from crawl4ai import AsyncWebCrawler, CacheMode
from loguru import logger
from tqdm import tqdm
from zenml.steps import step

from second_brain.domain import Page, PageMetadata


@step
def crawl(pages: list[Page]) -> list[Page]:
    """Crawl pages and their child URLs.

    Args:
        pages: List of pages to crawl

    Returns:
        list[Page]: List of original pages plus crawled child pages
    """

    crawler = Crawl4AICrawler()
    augmented_pages = pages.copy()

    for page in tqdm(pages, desc="Crawling pages"):
        child_pages = crawler(page)
        augmented_pages.extend(child_pages)

    return list(set(augmented_pages))


class Crawl4AICrawler:
    def __init__(self, max_concurrent_requests: int = 10) -> None:
        self.max_concurrent_requests = max_concurrent_requests

    def __call__(self, page: Page) -> list[Page]:
        content = asyncio.run(self.__crawl(page))

        return content

    async def __crawl(self, page: Page) -> list[Page]:
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        async with AsyncWebCrawler(cache_mode=CacheMode.BYPASS) as crawler:
            tasks = [
                self.__crawl_url(crawler, page, url, semaphore)
                for url in page.child_urls
            ]
            results = await asyncio.gather(*tasks)

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
        page: Page,
        url: str,
        semaphore: asyncio.Semaphore,
    ) -> Page | None:
        async with semaphore:
            result = await crawler.arun(
                url=url,
            )
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

            return Page(
                metadata=PageMetadata(
                    id=url,
                    url=url,
                    title=title,
                    properties=result.metadata or {},
                ),
                parent_metadata=page.metadata,
                content=str(result.markdown),
                child_urls=child_links,
            )
