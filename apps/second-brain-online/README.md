# Production LLM RAG Course Setup Guide

## Installation

To set it up first deactivate any active virtual environment and move to the second-brain-online directory:
```bash
deactivate
cd apps/second-brain-online
```

Then create a virtual environment and install the dependencies:
```bash
uv venv .venv-online
. ./.venv-online/bin/activate
uv pip install -e .
```

### Lesson 6

Quickly test the agent from the CLI with a predefined query:
```bash
make run_agent_query RETRIEVER_CONFIG=configs/compute_rag_vector_index_openai_parent.yaml
```

> [!IMPORTANT]
> Be sure that the retriever config is the exact same one as the one used in Module 5 during the RAG feature pipeline to populate the vector database. If they don't match, the used retriever will use different settings resulting in errors or unexpected results. Here is a quick reminder of when to use which config:
> - Parent Retrieval with OpenAI models:  `configs/compute_rag_vector_index_openai_parent.yaml`
> - Simple Contextual Retrieval with OpenAI models: `configs/compute_rag_vector_index_openai_contextual_simple.yaml`
> - Simple Contextual Retrieval with Hugging Face models: `configs/compute_rag_vector_index_huggingface_contextual_simple.yaml`
> - Full-fledged Contextual Retrieval with OpenAI models: `configs/compute_rag_vector_index_openai_contextual.yaml`

Spin-up the Gradio UI to test the agent with a custom queries:
```bash
make run_agent_app RETRIEVER_CONFIG=configs/compute_rag_vector_index_openai_parent.yaml
```

Evaluate the agent with our predefined evaluation queries (found under `tools/evaluate_app.py`):
```bash
make evaluate_agent RETRIEVER_CONFIG=configs/compute_rag_vector_index_openai_parent.yaml
```

For running the evaluation, plus playing around with the agent (~20 queries), the costs and running time are:
- Running costs OpenAI: ~$0.5
- Running costs Hugging Face Dedicated Endpoints (optional - you can use only the OpenAI models for summarization): it costs $1 / hour - it will cost you between $1 and $2 
- Running time evaluation: ~15 minutes (the AI Assistant runs in real-time)
