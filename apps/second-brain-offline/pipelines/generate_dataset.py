from pathlib import Path

from zenml import pipeline

from steps.generate_dataset import generate_summary_dataset
from steps.infrastructure import (
    fetch_from_mongodb,
    push_to_huggingface,
    save_dataset_to_disk,
)


@pipeline
def generate_dataset(
    extract_collection_name: str,
    load_dataset_id: str,
    fetch_limit: int = 1000,
    summarization_agent_model_id: str = "gpt-4o-mini",
    summarization_agent_mock: bool = False,
    val_split_ratio: float = 0.1,
    test_split_ratio: float = 0.1,
    max_workers: int = 10,
    data_dir: Path = Path("data/"),
    summarization_max_characters: int = 1000,
) -> None:
    documents = fetch_from_mongodb(
        collection_name=extract_collection_name, limit=fetch_limit
    )

    dataset = generate_summary_dataset(
        documents=documents,
        summarization_model=summarization_agent_model_id,
        val_split_ratio=val_split_ratio,
        test_split_ratio=test_split_ratio,
        max_workers=max_workers,
        mock=summarization_agent_mock,
        summarization_max_characters=summarization_max_characters,
    )

    push_to_huggingface(dataset, load_dataset_id)
    save_dataset_to_disk(dataset, output_dir=data_dir / "datasets" / load_dataset_id)
