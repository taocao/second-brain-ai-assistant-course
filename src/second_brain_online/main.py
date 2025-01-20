import os
import sys
from loguru import logger
from typing import List, Dict
import gradio as gr
from gradio.themes import Base
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_mongodb.retrievers import (
    MongoDBAtlasParentDocumentRetriever,
)

sys.path.append("../../src")
from second_brain.config import settings
from second_brain.infrastructure.mongo import MongoDBService
from second_brain.application.rag import get_splitter
from second_brain.application.rag.embeddings import EmbeddingModelBuilder

from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../../.env")

# Initialize MongoDB client
MONGODB_URI = os.getenv("MONGODB_OFFLINE_URI")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME")
MONGODB_COLLECTION_NAME_RAG = os.getenv("MONGODB_COLLECTION_NAME_RAG")

# Initialize embeddings
embedding_model = EmbeddingModelBuilder().get_model()

# Initialize the parent document retriever
parent_doc_retriever = MongoDBAtlasParentDocumentRetriever.from_connection_string(
    connection_string=settings.MONGODB_URI,
    embedding_model=embedding_model,
    child_splitter=get_splitter(200),
    parent_splitter=get_splitter(800),
    database_name=settings.MONGODB_DATABASE_NAME,
    collection_name="rag_data",
    text_key="page_content",
    search_kwargs={"k": 10},
)

def format_documents(docs: List[Document]) -> str:
    """Format documents for display."""
    formatted_results = []
    for i, doc in enumerate(docs, 1):
        title = doc.metadata.get('title', 'No title')
        url = doc.metadata.get('url', 'No URL')
        
        formatted_doc = f"Document {i}:\n"
        formatted_doc += f"Title: {title}\n"
        formatted_doc += f"Content: {doc.page_content[:500]}...\n"  # Truncate content for readability
        if url:
            formatted_doc += f"Source: {url}"
        
        formatted_results.append(formatted_doc)
    return "\n---\n".join(formatted_results)

def query_data(question: str):
    """Process user query and return both raw results and RAG response."""
    try:
        # Retrieve documents
        raw_docs = parent_doc_retriever.invoke(question)
        direct_response = format_documents(raw_docs)

        # Setup RAG chain
        retrieve = {
            "context": parent_doc_retriever 
            | (lambda docs: "\n\n".join([d.page_content for d in docs])),
            "question": RunnablePassthrough(),
        }

        template = """Answer the question based only on the following context. If no context is provided, respond with I DON'T KNOW: \
        {context}

        Question: {question}
        """
        chain = (
            retrieve
            | ChatPromptTemplate.from_template(template)
            | ChatOpenAI(temperature=0, model="gpt-4o-2024-11-20")
            | StrOutputParser()
        )

        rag_response = chain.invoke(question)

        
        return direct_response, rag_response

    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        print(error_msg)
        return error_msg, error_msg

# Create Gradio UI
with gr.Blocks(theme=Base(), title="Second Brain QA System") as demo:
    gr.Markdown(
        """
        # Second Brain Question Answering System
        Leveraging MongoDB and RAG Architecture.
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

    # Button click action
    button.click(query_data, textbox, outputs=[output1, output2])

if __name__ == "__main__":
    demo.launch()
