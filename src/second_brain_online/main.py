"""
Main module for the Second Brain Question Answering System.

This module implements a RAG (Retrieval Augmented Generation) based QA system using
MongoDB Atlas and OpenAI's language models. It provides a web interface using Gradio
for users to interact with their stored knowledge base.

sample search for gradio: How can I optimize LLMs for inference?
"""

### APP WORKFLOW: Second Brain QA System Process Flow
"""
1. User Input Phase:
   - User enters a question through the Gradio web interface
   - Question is passed to the SmolAgent-based processing function

2. Query Routing Phase:
   - System determines whether the query requires direct LLM inference or retrieval-augmented generation (RAG).

3. Document Retrieval Phase:
   - If RAG is required, the system connects to MongoDB Atlas using secure credentials
   - Question is converted to embeddings (numerical representations)
   - MongoDB Atlas searches for relevant documents using these embeddings
   - Most similar documents are retrieved and formatted for display

4. Response Generation Phase:
   - Retrieved documents are combined into context
   - Question and context are formatted into a prompt
   - Prompt is sent to OpenAI's GPT model
   - Model generates a response based on the provided context

5. Error Handling:
   - All operations are wrapped in try-except blocks
   - Errors are logged using loguru
   - User-friendly error messages are displayed if something goes wrong

Key Components:
- MongoDB Atlas: Document storage and vector search
- OpenAI GPT: Natural language processing
- Gradio: Web interface
- SmolAgents: Tool orchestration and workflow control
"""

### IMPORTS: Core dependencies and type hints
import os
import sys
from typing import List, Dict, Tuple, Optional
from loguru import logger
import gradio as gr
from gradio.themes import Base
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_mongodb.retrievers import MongoDBAtlasParentDocumentRetriever

import opik
from opik import track, opik_context
from opik.evaluation import evaluate
from opik.evaluation.metrics import AnswerRelevance, Hallucination, Moderation

from smolagents import Tool, CodeAgent, LiteLLMModel

from dotenv import load_dotenv

#note: the following sys.path.append is not recommended for production code, we'll use it as this is development code for learning 
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

# OpenAI API configuration
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

### TOOL DEFINITIONS
class MongoDBRetrieverTool(Tool):
    name = "retriever"
    description = "Retrieve documents from MongoDB Atlas using semantic search."
    inputs = {"query": {"type": "string", "description": "User's query."}}
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.retriever = self.initialize_retriever()
    @track
    def initialize_retriever(self) -> MongoDBAtlasParentDocumentRetriever:
        """
        Initialize the MongoDB Atlas document retriever with embedding model.
        
        Returns:
            ParentDocumentRetriever: Configured retriever instance
        
        Note:
            This function sets up the document retriever with specific chunk sizes
            for both parent and child documents, optimizing for retrieval quality.
        """
        embedding_model = EmbeddingModelBuilder().get_model()

        return MongoDBAtlasParentDocumentRetriever.from_connection_string(
            connection_string=settings.MONGODB_URI,
            embedding_model=embedding_model,
            child_splitter=get_splitter(200),  # Smaller chunks for precise matching
            parent_splitter=get_splitter(800),  # Larger chunks for context
            database_name=settings.MONGODB_DATABASE_NAME,
            collection_name="rag_data",
            text_key="page_content",
            search_kwargs={"k": 10},  # Number of documents to retrieve
        )
    @track
    def forward(self, query: str) -> str:
        try:
            raw_docs = self.retriever.invoke(query)
            return "\nRetrieved Documents:\n" + "\n\n".join([
                f"Document {i + 1}: {doc.page_content[:500]}..." for i, doc in enumerate(raw_docs)
            ])
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return "Error retrieving documents."

retriever_tool = MongoDBRetrieverTool()

# Define the LLM Model
model = LiteLLMModel(
    model_id="gpt-4o-mini",
    api_base="https://api.openai.com/v1",
    api_key=OPENAI_API_KEY
)

# Create the CodeAgent with tools and model

agent = CodeAgent(
    tools=[retriever_tool],
    model=model,
    max_steps=2,
    verbosity_level=2
)

### QUERY PROCESSING FUNCTION
@track(name=OPIK_APP_NAME)
def process_query_with_agent(question: str) -> Tuple[str, str]:
    """
    Process user query with the SmolAgent framework, dynamically routing to RAG or LLM.

    Args:
        question (str): User's input question.

    Returns:
        Tuple[str, str]: (retrieved documents, AI-generated response).
    """
    try:
        # Run the agent
        response = agent.run(f"Answer the query: {question}")
        
        # Extract retrieved documents from the response
        retrieved_docs = retriever_tool.forward(question)
        
        # Return both retrieved documents and AI response
        return retrieved_docs, response
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        logger.error(error_msg)
        return error_msg, error_msg


### UI: Gradio interface setup
def create_gradio_interface() -> gr.Blocks:
    """
    Create and configure the Gradio web interface.
    
    Returns:
        gr.Blocks: Configured Gradio interface
    """
    with gr.Blocks(theme=Base(), title="Second Brain QA System") as demo:
        gr.Markdown(
            """
            # Second Brain Question Answering System
            Leveraging MongoDB, OpenAI, and SmolAgents.
            """
        )

        textbox = gr.Textbox(
            label="Enter your Question:",
            placeholder="Ask me anything about the content in your Second Brain..."
        )

        with gr.Row():
            button = gr.Button("Submit", variant="primary")

        with gr.Column():
            output1 = gr.Textbox(
                lines=10,
                max_lines=20,
                label="Retrieved Documents:",
                show_copy_button=True
            )

            output2 = gr.Textbox(
                lines=8,
                max_lines=15,
                label="AI Response:",
                show_copy_button=True
            )

        button.click(process_query_with_agent, textbox, outputs=[output1, output2])
        
    return demo

### MAIN: Application entry point
if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch()
