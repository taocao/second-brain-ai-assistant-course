from zenml.steps import get_step_context, step

from second_brain.domain import Document
from second_brain.infrastructure.mongo import MongoDBService


@step
def fetch_from_mongodb(limit: int, collection_name: str) -> list[dict]:
    with MongoDBService(model=Document, collection_name=collection_name) as service:
        documents = service.fetch_documents(limit, query={})

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="fetched_documents",
        metadata={
            "len_documents": len(documents),
        },
    )

    return documents
