from zenml.steps import step

from second_brain.entities.page import Page


@step
def crawl(pages: list[Page]) -> list[dict]:
    return [page.model_dump() for page in pages]
