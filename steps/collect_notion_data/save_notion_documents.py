import shutil
from pathlib import Path

from zenml import step

from second_brain.domain import Document


@step
def save_notion_documents(
    documents: dict[str, Document],
    output_dir: Path,
) -> str:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    for document_id, document in documents.items():
        file_path = output_dir / f"{document_id}.json"
        document.write(file_path, obfuscate=True, also_save_as_txt=True)

    return str(output_dir)
