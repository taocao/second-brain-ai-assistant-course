import sys
import os
from loguru import logger
import openai
from pymongo import MongoClient
from opik import Opik
import opik
from opik import track, opik_context
from opik.evaluation import evaluate
from opik.evaluation.metrics import (
    AnswerRelevance,
    Hallucination,
    Moderation,
    ContextRecall,
    ContextPrecision
)
from openai import OpenAI
from langchain_mongodb.retrievers import MongoDBAtlasParentDocumentRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from opik.integrations.openai import track_openai
import json
from pprint import pformat

sys.path.append("../../src")
from second_brain.config import settings
from second_brain.infrastructure.mongo import MongoDBService
from second_brain.application.rag import get_splitter
from second_brain.application.rag.embeddings import EmbeddingModelBuilder

### CONFIGURATION: Environment and settings initialization
# Load environment variables
load_dotenv(dotenv_path="../../.env")

# MongoDB configuration
MONGODB_URI: str = os.getenv("MONGODB_OFFLINE_URI", "")
MONGODB_DATABASE_NAME: str = os.getenv("MONGODB_DATABASE_NAME", "")
MONGODB_COLLECTION_NAME_RAG: str = os.getenv("MONGODB_COLLECTION_NAME_RAG", "")

# opik
OPIK_API_KEY: str = os.getenv("OPIK_API_KEY", "")
OPIK_WORKSPACE: str = os.getenv("OPIK_WORKSPACE", "")
OPIK_APP_NAME: str = os.getenv("OPIK_APP_NAME", "")
OPIK_URL_OVERRIDE: str = os.getenv("OPIK_URL_OVERRIDE", "") 
OPIK_EVAL_DATASET: str = os.getenv("OPIK_EVAL_DATASET", "")

# openai
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_ID: str = os.getenv("OPENAI_MODEL_ID", "")

# Connect to MongoDB
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[MONGODB_DATABASE_NAME]
collection = db[MONGODB_COLLECTION_NAME_RAG]

# Initialize tracked OpenAI Client
openai_client = track_openai(OpenAI(api_key=OPENAI_API_KEY))

@track
def initialize_retriever() -> MongoDBAtlasParentDocumentRetriever:
    """Initialize the MongoDB Atlas document retriever with embedding model."""
    logger.info("Initializing retriever with configuration:")
    logger.info(f"Database: {MONGODB_DATABASE_NAME}")
    logger.info(f"Collection: {MONGODB_COLLECTION_NAME_RAG}")
    
    opik_context.update_current_trace(
        tags=["retriever_initialization"],
        metadata={
            "database": MONGODB_DATABASE_NAME,
            "collection": MONGODB_COLLECTION_NAME_RAG,
            "chunk_size": 200,
            "parent_chunk_size": 800
        }
    )
    
    embedding_model = EmbeddingModelBuilder().get_model()
    
    retriever = MongoDBAtlasParentDocumentRetriever.from_connection_string(
        connection_string=MONGODB_URI,
        embedding_model=embedding_model,
        child_splitter=get_splitter(200),
        parent_splitter=get_splitter(800),
        database_name=MONGODB_DATABASE_NAME,
        collection_name=MONGODB_COLLECTION_NAME_RAG,
        text_key="page_content",
        search_kwargs={"k": 10},
    )
    logger.info("Retriever initialized successfully")
    return retriever

@track(name="generate_prompts")
def generate_prompts_from_db(collection):
    """Generate prompts from MongoDB data."""
    logger.info("Starting prompt generation from database")
    prompts = []
    cursor = collection.find({"embedding": {"$exists": True}}, {"page_content": 1})
    
    opik_context.update_current_trace(
        tags=["prompt_generation"],
        metadata={"collection": collection.name}
    )
    
    for document in cursor:
        if "page_content" in document and document["page_content"]:
            content_snippet = document["page_content"][:500].replace("\n", " ").strip()
            prompt = (
                f"Based on this text, provide a clear and concise explanation or summary:\n\n'{content_snippet}'"
            )
            prompts.append(prompt)
            logger.debug(f"Generated prompt from content: {content_snippet[:100]}...")
    
    logger.info(f"Generated {len(prompts)} prompts from database")
    if prompts:
        logger.debug("Sample prompt structure:")
        logger.debug(pformat(prompts[0]))
    
    opik_context.update_current_trace(
        metadata={"num_prompts_generated": len(prompts)}
    )
    return prompts

@track(name="generate_dataset_items")
def generate_dataset_items(prompts, retriever, max_iterations=None):
    """Generate dataset items using RAG pipeline matching production setup."""
    logger.info("Starting dataset item generation")
    dataset_items = []
    iteration_count = 0

    template = """Answer the question based only on the following context. 
    If no context is provided, respond with I DON'T KNOW:
    
    Context: {context}
    Question: {question}
    """

    for prompt in prompts:
        if max_iterations is not None and iteration_count >= max_iterations:
            logger.info(f"Reached the maximum iteration limit of {max_iterations}.")
            break

        try:
            opik_context.update_current_trace(
                tags=["rag_retrieve_context"],
                metadata={"prompt": prompt}
            )
            
            # Retrieve context using the retriever
            raw_docs = retriever.invoke(prompt)
            context = "\n\n".join([d.page_content for d in raw_docs])
            
            logger.debug(f"Retrieved context for prompt '{prompt[:50]}...':\n{context[:200]}...")
            
            opik_context.update_current_trace(
                tags=["rag_generate_answer"],
                metadata={
                    "context_length": len(context),
                    "num_docs": len(raw_docs)
                }
            )

            # Generate answer using the same pipeline as production
            chain = (
                ChatPromptTemplate.from_template(template)
                | ChatOpenAI(temperature=0, model=OPENAI_MODEL_ID)
                | StrOutputParser()
            )

            response = chain.invoke({
                "context": context,
                "question": prompt
            })

            # Create dataset item with proper structure
            dataset_item = {
                "user_question": prompt,
                "expected_output": {
                    "assistant_answer": response,
                    "context": context
                }
            }
            
            logger.debug("Generated dataset item structure:")
            logger.debug(json.dumps(dataset_item, indent=2))
            
            dataset_items.append(dataset_item)

        except Exception as e:
            logger.error(f"Error processing response for prompt: '{prompt}' - {e}")
            continue

        iteration_count += 1

    # Log final summary
    logger.info(f"Generated dataset items summary:")
    logger.info(f"Total items: {len(dataset_items)}")
    if dataset_items:
        logger.info("Sample item structure:")
        logger.info(json.dumps(dataset_items[0], indent=2))

    opik_context.update_current_trace(
        metadata={
            "total_items_generated": len(dataset_items),
            "iteration_count": iteration_count
        }
    )
    return dataset_items

def evaluation_task(x: dict) -> dict:
    """Transform dataset items for evaluation."""
    try:
        result = {
            "input": x["user_question"],
            "context": x["expected_output"]["context"],
            "output": x["expected_output"]["assistant_answer"]
        }
        logger.debug(f"Evaluation task transformation:\nInput: {x}\nOutput: {result}")
        return result
    except KeyError as e:
        logger.error(f"Key error in evaluation task: {e}")
        logger.error(f"Input structure: {json.dumps(x, indent=2)}")
        raise

@track(name="main")
def main():
    """Main execution function."""
    if OPIK_API_KEY == "" or OPIK_WORKSPACE == "" or OPIK_APP_NAME != "second_brain_course" or OPIK_URL_OVERRIDE == "":
        logger.warning("OPIK configuration is incomplete. Exiting...")
        exit()
    
    logger.info("Initializing Opik client...")
    opik.configure(use_local=False)
    opik_client = Opik()

    opik_context.update_current_trace(
        tags=["initialization"],
        metadata={
            "app_name": OPIK_APP_NAME,
            "workspace": OPIK_WORKSPACE
        }
    )

    # Initialize retriever
    parent_doc_retriever = initialize_retriever()

    # Get or create dataset
    dataset_name = OPIK_EVAL_DATASET
    dataset = opik_client.get_or_create_dataset(name=dataset_name)

    # Generate prompts and dataset items
    prompts = generate_prompts_from_db(collection)
    if not prompts:
        logger.error("No prompts could be generated from the database.")
        return

    dataset_items = generate_dataset_items(prompts, parent_doc_retriever, 5)

    # Setup evaluation
    scoring_metrics = [
        Hallucination(),
        AnswerRelevance(),
        Moderation()
    ]

    experiment_config = {
        "model_id": OPENAI_MODEL_ID,
        "embedding_model": "text-embedding-3-small",
        "retriever_config": {
            "chunk_size": 200,
            "parent_chunk_size": 800,
            "k": 10
        }
    }

    if dataset_items:
        # Log pre-evaluation state
        logger.info(f"\nPre-evaluation state:")
        logger.info(f"Dataset: {dataset_name}")
        logger.info(f"Items to evaluate: {len(dataset_items)}")
        logger.info(f"Metrics: {[m.__class__.__name__ for m in scoring_metrics]}")
        logger.info("Sample evaluation structure:")
        sample_eval = evaluation_task(dataset_items[0])
        logger.info(json.dumps(sample_eval, indent=2))

        dataset.insert(dataset_items)
        
        opik_context.update_current_trace(
            tags=["evaluation"],
            metadata={
                "dataset_name": dataset_name,
                "num_items": len(dataset_items),
                "metrics": [m.__class__.__name__ for m in scoring_metrics],
                "experiment_config": experiment_config
            }
        )

        logger.info("\nRunning evaluation...")
        evaluate(
            dataset=dataset,
            task=evaluation_task,
            scoring_metrics=scoring_metrics,
            experiment_config=experiment_config
        )
        logger.info("Evaluation complete.")
    else:
        logger.error("No dataset items were generated.")

if __name__ == "__main__":
    main()