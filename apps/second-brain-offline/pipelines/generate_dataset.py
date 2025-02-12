from pathlib import Path

from zenml import pipeline

from steps.generate_dataset import create_histograms, generate_summary_dataset
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
    summarization_max_characters: int = 256,
    val_split_ratio: float = 0.1,
    test_split_ratio: float = 0.1,
    min_document_characters: int = 50,
    min_quality_score: float = 0.3,
    augmentation_loops: int = 4,
    max_workers: int = 10,
    data_dir: Path = Path("data/"),
) -> None:
    documents = fetch_from_mongodb(
        collection_name=extract_collection_name, limit=fetch_limit
    )
    create_histograms(documents)

    dataset = generate_summary_dataset(
        documents=documents,
        summarization_model=summarization_agent_model_id,
        val_split_ratio=val_split_ratio,
        test_split_ratio=test_split_ratio,
        min_document_characters=min_document_characters,
        min_quality_score=min_quality_score,
        augmentation_loops=augmentation_loops,
        max_workers=max_workers,
        mock=summarization_agent_mock,
        summarization_max_characters=summarization_max_characters,
    )

    push_to_huggingface(dataset, load_dataset_id)
    save_dataset_to_disk(dataset, output_dir=data_dir / "datasets" / load_dataset_id)
