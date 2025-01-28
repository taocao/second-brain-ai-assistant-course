from loguru import logger
from typing_extensions import Annotated
from zenml import get_step_context, step

from second_brain_offline.application.agents.quality import QualityScoreAgent
from second_brain_offline.domain import Document


@step
def add_quality_score(
    documents: list[Document],
    model_id: str = "gpt-4o-mini",
    mock: bool = False,
    max_workers: int = 10,
) -> Annotated[list[Document], "enhanced_documents"]:
    """Enhances documents by adding quality scores using a quality scoring agent.

    Args:
        documents (list[Document]): List of documents to evaluate for quality.
        model_id (str, optional): ID of the model to use for quality checking.
            Defaults to "gpt-4o-mini".
        mock (bool, optional): Whether to use mock responses instead of real model calls.
            Defaults to False.
        max_workers (int, optional): Maximum number of concurrent quality checks.
            Defaults to 10.

    Returns:
        Annotated[list[Document], "enhanced_documents"]: Documents enhanced with quality scores.
            The annotation provides metadata about the transformation.
    """

    quality_agent = QualityScoreAgent(
        model_id=model_id, mock=mock, max_concurrent_requests=max_workers
    )
    enhanced_documents: list[Document] = quality_agent(documents)

    len_documents = len(documents)
    len_documents_with_scores = len(
        [doc for doc in enhanced_documents if doc.content_quality_score is not None]
    )
    logger.info(f"Total documents: {len_documents}")
    logger.info(f"Total documents that were enhanced: {len_documents_with_scores}")

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="enhanced_documents",
        metadata={
            "len_documents": len_documents,
            "len_documents_with_scores": len_documents_with_scores,
        },
    )

    return enhanced_documents
