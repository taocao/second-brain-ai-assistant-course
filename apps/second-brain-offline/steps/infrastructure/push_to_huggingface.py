from loguru import logger
from typing_extensions import Annotated
from zenml import get_step_context, step

from second_brain_offline.config import settings
from second_brain_offline.domain import InstructDataset


@step
def push_to_huggingface(
    dataset: Annotated[InstructDataset, "instruct_dataset"],
    dataset_id: Annotated[str, "dataset_id"],
) -> Annotated[str, "output"]:
    assert settings.HUGGINGFACE_ACCESS_TOKEN is not None, (
        "Huggingface access token must be provided for pushing to Huggingface"
    )

    logger.info(f"Pushing dataset {dataset_id} to Hugging Face.")

    huggingface_dataset = dataset.to_huggingface()
    huggingface_dataset.push_to_hub(dataset_id, token=settings.HUGGINGFACE_ACCESS_TOKEN)

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="output",
        metadata={
            "dataset_id": dataset_id,
            "train_samples": len(huggingface_dataset["train"]),
            "validation_samples": len(huggingface_dataset["validation"]),
            "test_samples": len(huggingface_dataset["test"]),
        },
    )

    return dataset_id
