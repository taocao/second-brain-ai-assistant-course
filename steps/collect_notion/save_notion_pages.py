import shutil
from pathlib import Path

from zenml import step

from second_brain.entities import Page


@step
def save_notion_pages(
    database_id: str,
    pages: dict[str, Page],
) -> None:
    output_dir = Path("data") / database_id
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    for page_id, page in pages.items():
        file_path = output_dir / f"{page_id}.json"
        page.write(file_path)
