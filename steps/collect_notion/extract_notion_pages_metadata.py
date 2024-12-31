from typing_extensions import Annotated
from zenml import step


@step
def extract_notion_pages_metadata(
    database_id: str,
) -> Annotated[list[str], "notion_pages_metadata"]:
    return []
