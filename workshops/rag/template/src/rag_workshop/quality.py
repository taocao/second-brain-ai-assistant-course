from langchain_core.documents import Document
from pydantic import BaseModel


class HeuristicQualityJudge:
    """A rule-based agent for evaluating document quality based on simple heuristics.

    Evaluates document quality by analyzing the ratio of URL content to total content length.
    Documents with high URL content ratios receive lower quality scores.
    """

    def __call__(self, documents: list[Document]) -> list[Document]:
        """Process documents for quality scoring using heuristic rules.

        Args:
            documents: List of Document objects to evaluate based on URL content ratio.

        Returns:
            The input documents with quality scores added to their metadata under the
            'quality_score' key where URL content ratio thresholds are met.
        """

        scored_documents = [self.__score_document(document) for document in documents]

        return scored_documents

    def __score_document(self, document: Document) -> Document:
        """Score a single document based on URL content ratio.

        Args:
            document: The Document object to score.

        Returns:
            The input document with quality score added to metadata under 'quality_score'
            key if URL content ratio thresholds are met. Empty documents receive a score
            of 0.0.
        """

        # TODO: Implement heuristic quality scoring

        return document


class QualityScoreResponseFormat(BaseModel):
    """Format for quality score responses from the language model.

    Attributes:
        score: A float between 0.0 and 1.0 representing the quality score.
    """

    score: float


class QualityScoreJudge:
    """Evaluates the quality of documents using LiteLLM with async support.

    Uses language models through LiteLLM to evaluate document quality based on relevance,
    factual accuracy, and information coherence.

    Attributes:
        model_id: The ID of the language model to use for evaluation.
    """

    SYSTEM_PROMPT_TEMPLATE = """You are an expert judge tasked with evaluating the quality of a given DOCUMENT.

Guidelines:
1. Evaluate the DOCUMENT based on generally accepted facts and reliable information.
2. Evaluate that the DOCUMENT contains relevant information and not only links or error messages.
3. Check that the DOCUMENT doesn't oversimplify or generalize information in a way that changes its meaning or accuracy.

Analyze the text thoroughly and assign a quality score between 0 and 1, where:
- **0.0**: The DOCUMENT is completely irrelevant containing only noise such as links or error messages
- **0.1 - 0.7**: The DOCUMENT is partially relevant containing some relevant information checking partially guidelines
- **0.8 - 1.0**: The DOCUMENT is entirely relevant containing all relevant information following the guidelines

It is crucial that you return only the score in the following JSON format:
{{
    "score": <your score between 0.0 and 1.0>
}}

DOCUMENT:
{document}
"""

    def __init__(
        self,
        model_id: str = "gpt-4o-mini",
    ) -> None:
        self.model_id = model_id

    def __call__(self, documents: list[Document]) -> list[Document]:
        """Process a batch of documents for quality scoring.

        Args:
            documents: List of Document objects to evaluate for quality.

        Returns:
            A list of Document objects with quality scores added to their metadata under
            the 'quality_score' key. Scores range from 0.0 to 1.0.
        """

        scored_documents = [self.__score_document(document) for document in documents]

        return scored_documents

    def __score_document(self, document: Document) -> Document:
        """Generate a quality score for a single document.

        Args:
            document: The Document object to evaluate.

        Returns:
            The input Document with a quality score added to its metadata under the
            'quality_score' key. If scoring fails, the document is returned unchanged
            and a warning is logged.
        """

        # TODO: Implement quality scoring

        return document

    def _parse_model_output(
        self, answer: str | None
    ) -> QualityScoreResponseFormat | None:
        """Parse the model's output into a structured format.

        Args:
            answer: Raw string output from the language model containing a JSON
                response with a 'score' field.

        Returns:
            A QualityScoreResponseFormat object containing the parsed score if successful,
            None if parsing fails.
        """

        # TODO: Implement model output parsing

        return None
