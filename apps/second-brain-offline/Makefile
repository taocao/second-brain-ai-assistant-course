ifeq (,$(wildcard .env))
$(error .env file is missing. Please create one based on .env.example. Run: "cp .env.example .env" and fill in the missing values.)
endif

include .env

export UV_PROJECT_ENVIRONMENT=.venv-offline
export PYTHONPATH = .

# --- Default Values ---

CHECK_DIRS := .
AWS_S3_BUCKET_NAME := decodingml-public-data
NOTION_LOCAL_DATA_PATH := data/notion
CRAWLED_LOCAL_DATA_PATH := data/crawled


# --- Utilities ---

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# --- Infrastructure --- 

local-docker-infrastructure-up:
	docker compose -f ../infrastructure/docker/docker-compose.yml up --build -d 

local-docker-infrastructure-stop:
	docker compose -f ../infrastructure/docker/docker-compose.yml stop

local-zenml-server-up:
ifeq ($(shell uname), Darwin)
	OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES uv run zenml login --local
else
	uv run zenml login --local
endif

local-zenml-server-stop:
	uv run zenml logout --local

local-infrastructure-up: local-docker-infrastructure-up local-zenml-server-stop local-zenml-server-up

local-infrastructure-stop: local-docker-infrastructure-stop local-zenml-server-stop

# --- AWS ---

validate_aws_boto3:
	@echo "Validating AWS Boto3 credentials..."
	uv run python -m tools.validate_aws_boto3

s3-upload-notion-dataset:  # Upload raw Notion dataset from local folder to S3
	@echo "Uploading raw Notion dataset to S3 bucket: $(AWS_S3_BUCKET_NAME)/second_brain_course/notion"
	uv run python -m tools.use_s3 upload $(NOTION_LOCAL_DATA_PATH) $(AWS_S3_BUCKET_NAME) --s3-prefix second_brain_course/notion

s3-download-notion-dataset:  # Download raw Notion dataset from S3 to local folder
	@echo "Downloading raw Notion dataset from S3 bucket: $(AWS_S3_BUCKET_NAME)/second_brain_course/notion/notion.zip"
	uv run python -m tools.use_s3 download $(AWS_S3_BUCKET_NAME) second_brain_course/notion/notion.zip $(NOTION_LOCAL_DATA_PATH) --no-sign-request

s3-upload-crawled-dataset:  # Upload processed crawled dataset from local folder to S3
	@echo "Uploading crawled dataset to S3 bucket: $(AWS_S3_BUCKET_NAME)/second_brain_course/crawled"
	uv run python -m tools.use_s3 upload $(CRAWLED_LOCAL_DATA_PATH) $(AWS_S3_BUCKET_NAME) --s3-prefix second_brain_course/crawled

s3-download-crawled-dataset:  # Download processed crawled dataset from S3 to local folder
	@echo "Downloading crawled dataset from S3 bucket: $(AWS_S3_BUCKET_NAME)/second_brain_course/crawled/crawled.zip"
	uv run python -m tools.use_s3 download $(AWS_S3_BUCKET_NAME) second_brain_course/crawled/crawled.zip $(CRAWLED_LOCAL_DATA_PATH) --no-sign-request

download-notion-dataset: s3-download-notion-dataset

download-crawled-dataset: s3-download-crawled-dataset

# --- Offline ML Pipelines ---

collect-notion-data-pipeline:
	uv run python -m tools.run --run-collect-notion-data-pipeline --no-cache

etl-pipeline:
	uv run python -m tools.run --run-etl-pipeline --no-cache

etl-precomputed-pipeline:
	uv run python -m tools.run --run-etl-precomputed-pipeline --no-cache

generate-dataset-pipeline:
	uv run python -m tools.run --run-generate-dataset-pipeline --no-cache

compute-rag-vector-index-huggingface-contextual-simple-pipeline:
	uv run python -m tools.run --run-compute-rag-vector-index-huggingface-contextual-simple-pipeline --no-cache

compute-rag-vector-index-openai-contextual-simple-pipeline:
	uv run python -m tools.run --run-compute-rag-vector-index-openai-contextual-simple-pipeline --no-cache

compute-rag-vector-index-openai-contextual-pipeline:
	uv run python -m tools.run --run-compute-rag-vector-index-openai-contextual-pipeline --no-cache

compute-rag-vector-index-openai-parent-pipeline:
	uv run python -m tools.run --run-compute-rag-vector-index-openai-parent-pipeline --no-cache

delete-rag-collection:
	uv run python -m tools.delete_rag_collection

# --- Check Deployments ---

check-huggingface-dedicated-endpoint:
	uv run python -m tools.call_huggingface_dedicated_endpoint

# --- Check RAG Ingestion ---

check-rag-huggingface-contextual-simple:
	uv run python -m tools.rag --config ./configs/compute_rag_vector_index_huggingface_contextual_simple.yaml

check-rag-openai-contextual-simple:
	uv run python -m tools.rag --config ./configs/compute_rag_vector_index_openai_contextual_simple.yaml

check-rag-openai-contextual:
	uv run python -m tools.rag --config ./configs/compute_rag_vector_index_openai_contextual.yaml

check-rag-openai-parent:
	uv run python -m tools.rag --config ./configs/compute_rag_vector_index_openai_parent.yaml


# --- Tests ---

test:
	uv run pytest tests -v

test-s3-download:
	uv run pytest tests/test_s3.py -v

test-download-notion-dataset:
	uv run pytest tests/test_download_notion_dataset.py -v

test-download-crawled-dataset:
	uv run pytest tests/test_download_crawled_dataset.py -v
	
# --- QA ---

format-fix:
	uv run ruff format $(CHECK_DIRS)
	uv run ruff check --select I --fix 

lint-fix:
	uv run ruff check --fix

format-check:
	uv run ruff format --check $(CHECK_DIRS) 
	uv run ruff check -e
	uv run ruff check --select I -e

lint-check:
	uv run ruff check $(CHECK_DIRS)
