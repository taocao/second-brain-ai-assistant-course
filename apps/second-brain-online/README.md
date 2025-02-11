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

Quickly test the agent from the CLI:
```bash
make run_agent_query RETRIEVER_CONFIG=configs/compute_rag_vector_index_openai_parent.yaml
```

> [!IMPORTANT]
> Be sure that the retriever config is the exact same one as the one used in Module 5 during the RAG feature pipeline to populate the vector database. If they don't match, the used retriever will use different settings resulting in errors or unexpected results.

Spin-up the Gradio UI:
```bash
make run_agent_app RETRIEVER_CONFIG=configs/compute_rag_vector_index_openai_parent.yaml
```

Evaluate the agent:
```bash
make evaluate_agent RETRIEVER_CONFIG=configs/compute_rag_vector_index_openai_parent.yaml
```
