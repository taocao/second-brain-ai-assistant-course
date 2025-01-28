import copy
from typing import Callable

from loguru import logger

from second_brain_offline.application.agents import SummarizationAgent
from second_brain_offline.domain import Document, InstructDataset
from second_brain_offline.domain.dataset import InstructDatasetSample


class SummarizationDatasetGenerator:
    """Generates an instruction dataset from documents by creating summaries.

    This class takes a list of documents and generates summaries using a specified
    language model. The resulting dataset can be split into training, validation,
    and test sets.

    Attributes:
        summarization_model: Name/ID of the model to use for summarization.
        summarization_max_characters: Maximum number of characters for the summary.
        val_split_ratio: Fraction of data to use for validation (0-1).
        test_split_ratio: Fraction of data to use for testing (0-1).
        max_workers: Maximum number of parallel workers for processing.
        mock: If True, generates mock summaries instead of using the model.
    """

    def __init__(
        self,
        summarization_model: str,
        summarization_max_characters: int,
        val_split_ratio: float = 0.1,
        test_split_ratio: float = 0.1,
        max_workers: int = 10,
        mock: bool = False,
    ) -> None:
        self.summarization_model = summarization_model
        self.summarization_max_characters = summarization_max_characters
        self.val_split_ratio = val_split_ratio
        self.test_split_ratio = test_split_ratio
        self.max_workers = max_workers
        self.mock = mock

        self.pregeneration_filters: list[Callable[[Document], bool]] = [
            lambda document: len(document.content) > 100,
        ]
        self.postgeneration_filters: list[Callable[[Document], bool]] = [
            lambda document: document.summary is not None
            and len(document.summary) > 100
            and len(document.summary) < (self.summarization_max_characters * 1.2),
        ]

    def generate(self, documents: list[Document]) -> InstructDataset:
        """Generates an instruction dataset from the documents.

        The method filters, summarizes documents and converts them into instruction-answer pairs.
        Warns if input document count is less than recommended minimum of 10.

        Args:
            documents: List of Document objects to be processed into the dataset

        Returns:
            InstructDataset: A dataset containing instruction-answer pairs where:
                - instructions are document contents
                - answers are generated summaries
        """

        if len(documents) < 10:
            logger.warning(
                "Less than 10 documents to summarize. For accurate behavior we recommend having at least 10 documents."
            )

        filtered_summarized_documents = self.__summarize_documents(documents)
        instruct_dataset_samples = [
            self.__to_instruct_dataset_sample(summarized_document)
            for summarized_document in filtered_summarized_documents
            if summarized_document
        ]
        logger.info(f"Num instruct dataset samples: {len(instruct_dataset_samples)}")

        return InstructDataset.from_samples(
            samples=instruct_dataset_samples,
            val_split_ratio=self.val_split_ratio,
            test_split_ratio=self.test_split_ratio,
            seed=42,
        )

    def __summarize_documents(self, documents: list[Document]) -> list[Document]:
        """Summarizes the filtered documents using a summarization agent.

        Args:
            documents: List of documents to summarize

        Returns:
            list[Document]: List of documents with generated summaries that pass
                both pre and post-generation filters
        """

        logger.info(f"Num documents before pregeneration filtering: {len(documents)}")
        filtered_documents = self.filter_documents(
            self.pregeneration_filters, documents
        )
        logger.info(
            f"Num documents after pregeneration filtering: {len(filtered_documents)}"
        )
        summarized_documents: list[Document] = self.__augmented_summarization_loop(
            filtered_documents, loops=5
        )
        filtered_summarized_documents = self.filter_documents(
            self.postgeneration_filters, summarized_documents
        )
        logger.info(
            f"Num documents after postgeneration filtering: {len(filtered_summarized_documents)}"
        )

        return filtered_summarized_documents

    def __augmented_summarization_loop(
        self, documents: list[Document], loops: int = 3
    ) -> list[Document]:
        summarization_agent = SummarizationAgent(
            max_characters=self.summarization_max_characters,
            model_id=self.summarization_model,
            max_concurrent_requests=self.max_workers,
            mock=self.mock,
        )
        augmented_documents = []
        for i in range(loops):
            temperature = i * 0.5 / loops  # 0.0 to 0.5
            copied_documents = copy.deepcopy(documents)
            summarized_documents = summarization_agent(
                copied_documents, temperature=temperature
            )
            augmented_documents.extend(summarized_documents)

        return augmented_documents

    def filter_documents(
        self, filters: list[Callable[[Document], bool]], documents: list[Document]
    ) -> list[Document]:
        """Filters documents using provided filter functions.

        Args:
            filters: List of filter functions that take a Document and return bool
            documents: List of documents to filter

        Returns:
            list[Document]: Filtered list of documents that pass all filter functions
        """

        for document_filter in filters:
            documents = [
                document for document in documents if document_filter(document)
            ]

        return documents

    def __to_instruct_dataset_sample(self, document: Document) -> InstructDatasetSample:
        """Converts a summarized document to an instruction dataset sample.

        Args:
            document: A Document object containing both content and summary.

        Returns:
            An InstructDatasetSample with document content as instruction and
            summary as answer.

        Raises:
            AssertionError: If the document's summary is None.
        """

        assert document.summary is not None, "Document summary is None"

        return InstructDatasetSample(
            instruction=document.content,
            answer=document.summary,
        )
