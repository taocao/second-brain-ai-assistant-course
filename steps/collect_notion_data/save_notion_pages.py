import shutil
from pathlib import Path

from zenml import step

from second_brain.domain import Page


@step
def save_notion_pages(
    database_id: str,
    pages: dict[str, Page],
    output_dir: Path,
) -> str:
    database_output_dir = output_dir / database_id
    if database_output_dir.exists():
        shutil.rmtree(database_output_dir)
    database_output_dir.mkdir(parents=True)

    for page_id, page in pages.items():
        file_path = database_output_dir / f"{page_id}.json"
        page.write(file_path, obfuscate=True, also_save_as_txt=True)

    return str(database_output_dir)
