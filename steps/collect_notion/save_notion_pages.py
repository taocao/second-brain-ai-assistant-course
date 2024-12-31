from pathlib import Path

from zenml import step


@step
def save_notion_pages(
    database_id: str,
    pages: dict[str, str],
) -> None:
    output_dir = Path("data") / database_id
    output_dir.mkdir(parents=True, exist_ok=True)

    for page_name, content in pages.items():
        file_path = output_dir / f"{page_name}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
