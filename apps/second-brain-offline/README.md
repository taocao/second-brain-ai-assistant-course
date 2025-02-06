# 🚀 Installation and Usage Guide for the Second Brain Offline Module

This guide will help you set up and run the Second Brain Offline Module which contains the code for modules 1-5.

# 📑 Table of Contents

- [📋 Prerequisites](#-prerequisites)
- [🎯 Getting Started](#-getting-started)
- [📁 Project Structure](#-project-structure)
- [🏗️ Set Up Your Local Infrastructure](#-set-up-your-local-infrastructure)
- [⚡️ Running the Code for Each Lesson](#️-running-the-code-for-each-lesson)
- [🔧 Utlity Commands](#-utility-commands)

# 📋 Prerequisites

## Local Tools
You'll need the following tools installed locally:

| Tool | Version | Purpose | Installation Link |
|------|---------|---------|------------------|
| Python | 3.11 | Programming language runtime | [Download](https://www.python.org/downloads/) |
| uv | ≥ 0.4.30 | Python package installer and virtual environment manager | [Download](https://github.com/astral-sh/uv) |
| GNU Make | ≥ 3.81 | Build automation tool | [Download](https://www.gnu.org/software/make/) |
| Git | ≥2.44.0 | Version control | [Download](https://git-scm.com/downloads)

## Cloud Services
The project requires access to these cloud services:

| Service | Purpose | Cost | Required Credentials | Setup Guide |
|---------|---------|------|---------------------|-------------|
| [OpenAI API](https://openai.com/index/openai-api/) | LLM API for recommender system | Pay-per-use | `OPENAI_API_KEY` | [Quick Start Guide](https://platform.openai.com/docs/quickstart) |

# 🎯 Getting Started

## 1. Clone the Repository

Start by cloning the repository and navigating to the project directory:
```
git clone https://github.com/decodingml/second-brain-ai-assistant-course.git
cd second-brain-ai-assistant-course 
```

## 2. Installation

First deactivate any active virtual environment and move to the `second-brain-online` directory:
```bash
deactivate
cd apps/second-brain-offline
```

To install the dependencies and activate the virtual environment, run the following commands:

```bash
uv venv .venv-offline
. ./.venv-offline/bin/activate # or source ./.venv-offline/bin/activate
uv pip install -e .
```

Finish setting up `Crew4AI` for crawling:
```bash
# Run post-installation setup
uv pip install -U "crawl4ai==0.4.247" # We have to upgrade crawl4ai to support these CLI commands (we couldn't add it to pyproject.toml due to ZenML version incompatibility with Pydantic).
crawl4ai-setup

# Verify your installation
crawl4ai-doctor
```

> [!IMPORTANT]
> As crawling can often fail, both during installation and while running the crawling logic, you can skip the crawling step and use our pre-computed dataset. More on this in the [Running the ML pipelines / Lessons](#running-the-ml-pipelines--lessons) section.

After running the doctor command, you should see something like this:
```console
[INIT].... → Running Crawl4AI health check...
[INIT].... → Crawl4AI 0.4.247
[TEST].... ℹ Testing crawling capabilities...
[EXPORT].. ℹ Exporting PDF and taking screenshot took 0.84s
[FETCH]... ↓ https://crawl4ai.com... | Status: True | Time: 3.91s
[SCRAPE].. ◆ Processed https://crawl4ai.com... | Time: 11ms
[COMPLETE] ● https://crawl4ai.com... | Status: True | Total: 3.92s
[COMPLETE] ● ✅ Crawling test passed!
```
[More on installing Crawl4AI](https://docs.crawl4ai.com/core/installation/)

## 3. Environment Configuration

Before running any components:
1. Create your environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and configure the required credentials following the inline comments and the recommendations from the [Cloud Services](#-prerequisites) section.

# 📁 Project Structure

At Decoding ML we teach how to build production ML systems, thus the course follows the structure of a real-world Python project:

```bash
.
├── configs/                   # ZenML configuration files
├── pipelines/                 # ZenML ML pipeline definitions
├── src/second_brain_offline/  # Main package directory
│   ├── application/           # Application layer
│   ├── domain/                # Domain layer
│   ├── infrastructure/        # Infrastructure layer
│   ├── config.py              # Configuration settings
│   └── utils.py               # Utility functions
├── steps/                     # ZenML pipeline steps
├── tests/                     # Test files
├── tools/                     # Entrypoint scripts that use the Python package
├── .env.example               # Environment variables template
├── .python-version            # Python version specification
├── Makefile                   # Project commands
└── pyproject.toml             # Project dependencies
```

# 🏗️ Set Up Your Local Infrastructure

To start the local infrastructure (ZenML, MongoDB):
```bash
make local-infrastructure-up
```

To stop the local infrastructure (ZenML, MongoDB):
```bash
make local-infrastructure-down
```

# ⚡️ Running the Code for Each Module

## Module 1: Build your Second Brain AI assistant

Lesson: [Build your Second Brain AI assistant]()

No code to run for this lesson. Read the lesson to understand the problem and overall architecture of the Second Brain AI assistant.

## Module 2: ETL pipeline

### Prepare Notion data

Download our prepared Notion dataset from S3 (recommended):
```bash
make download-notion-dataset
# Validate using test: make test-download-notion-dataset
```

Or if you want to prepare your own Notion data (optional - if you want to use your own data):
```bash
make collect-notion-data-pipeline
```

### Run the ETL pipeline

Run the ETL pipeline to crawl, score and ingest the Notion data into MongoDB:
```bash
make etl-pipeline
# Validate using test: make test-etl-pipeline
```
Running costs: ~$0.5 </br>
Running time: ~30 minutes

If you want to avoid any costs or waiting times, you can use our pre-computed dataset to populate MongoDB. Also, as crawling can often fail, you can use this dataset to skip the crawling step:
```bash
make download-crawled-dataset
# Validate using test: make test-download-crawled-dataset
make etl-precomputed-pipeline
```

## Module 3: Generate Fine-tuning Dataset

```bash
make generate-dataset-pipeline
```
Running costs: ~$1.5 </br>
Running time: ~60 minutes

In case you want to avoid any costs or waiting times, you can use our pre-computed dataset available on Hugging Face, which is already set as default in future steps: [pauliusztin/second_brain_course_summarization_task](https://huggingface.co/datasets/pauliusztin/second_brain_course_summarization_task).

## Lesson 4: Fine-tuning and Evaluating Summarization LLM

This time we will use Notebooks, as they are popular when it comes to LLM fine-tuning.

| Purpose | Notebook | Useful Resources |
|---------|----------|------------------|
| Training | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/decodingml/second-brain-ai-assistant-course/blob/main/apps/second-brain-offline/src/second_brain_offline/application/models/finetuning.ipynb) | [Tracking training with an experiment tracker](https://www.comet.com/iusztinpaul/second-brain-course/f142e308313b4eedb298f15a34f5f0bb?compareXAxis=step&experiment-tab=panels&showOutliers=true&smoothing=0&xAxis=step) |
| Inference | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/decodingml/second-brain-ai-assistant-course/blob/main/apps/second-brain-offline/src/second_brain_offline/application/models/inference.ipynb) | - |
| Evaluation | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/decodingml/second-brain-ai-assistant-course/blob/main/apps/second-brain-offline/src/second_brain_offline/application/models/evaluate.ipynb) | - |


## Lesson 5: Compute RAG vector index

```bash
make compute-rag-vector-index-pipeline
```

## Lesson 6: Agentic App

The Agentic App sits in the online environment, which is implemented as a different Python application.

Go to the [apps/second-brain-online](../second-brain-online/) folder and follow the instructions there to set it up and run it.

# 🔧 Utlity Commands

## Formatting

```
make format-check
make format-fix
```

## Linting

```bash
make lint-check
make lint-fix
```

## Tests

```bash
make test
```

# 🧊 Notion (optional)

In case you want to use your own Notion data, you can follow these steps to set up an integration and read from your Notion database:

1. Go to [https://www.notion.so/profile].
2. Create an integration following [this tutorial](https://developers.notion.com/docs/authorization).
3. Copy your integration secret to programatically read from Notion.
4. Share your database with the integration:
   - Open your Notion database
   - Click the '...' menu in the top right
   - Click 'Add connections'
   - Select your integration
5. Get the correct database ID:
   - Open your database in Notion
   - Copy the ID from the URL: 
     ```
     https://www.notion.so/{workspace}/{database_id}?v={view_id}
     ```
   - The database ID is the part between the workspace name and the question mark
