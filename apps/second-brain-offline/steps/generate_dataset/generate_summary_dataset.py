from typing_extensions import Annotated
from zenml import step

from second_brain_offline.application.dataset import SummarizationDatasetGenerator
from second_brain_offline.domain import Document, InstructDataset


@step
def generate_summary_dataset(
    documents: list[Document],
    summarization_model: str,
    val_split_ratio: float = 0.1,
    test_split_ratio: float = 0.1,
    max_workers: int = 10,
    mock: bool = False,
    summarization_max_characters: int = 1000,
) -> Annotated[InstructDataset, "summary_dataset"]:
    dataset_generator = SummarizationDatasetGenerator(
        summarization_model=summarization_model,
        summarization_max_characters=summarization_max_characters,
        val_split_ratio=val_split_ratio,
        test_split_ratio=test_split_ratio,
        max_workers=max_workers,
        mock=mock,
    )
    dataset = dataset_generator.generate(documents=documents)

    return dataset
