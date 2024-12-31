from typing_extensions import Annotated
from zenml import step


@step
def extract_notion_pages(
    page_ids: list[str],
) -> Annotated[list[str], "pages"]:
    return []
