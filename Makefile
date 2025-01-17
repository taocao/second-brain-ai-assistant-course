ifeq (,$(wildcard .env))
$(error .env file is missing. Please create one based on .env.example)
endif

include .env

export PYTHONPATH = .

# --- Default Values ---

CHECK_DIRS := .
LOCAL_DATA_PATH := data


# --- Utilities ---

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# --- Infrastructure --- 

local-docker-infrastructure-up:
	docker compose up --build -d 

local-docker-infrastructure-up-development:
	docker compose watch

local-docker-infrastructure-stop:
	docker compose stop

local-zenml-server-up:
ifeq ($(shell uname), Darwin)
	OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES uv run zenml login --local
else
	uv run zenml login --local
endif

local-zenml-server-stop:
	uv run zenml logout --local

local-infrastructure-up: local-docker-infrastructure-up local-zenml-server-stop local-zenml-server-up

local-infrastructure-stop: local-docker-infrastructure-down local-zenml-server-down

# --- AWS ---

s3-upload:  # Upload a local folder to S3
	@echo "Uploading to S3 bucket: $(AWS_S3_BUCKET_NAME)"
	uv run python -m tools.use_s3 upload $(LOCAL_DATA_PATH) $(AWS_S3_BUCKET_NAME) --s3-prefix $(AWS_S3_PREFIX)

s3-download:  # Download from S3 to local folder using AWS 
	@echo "Downloading from S3 bucket: $(AWS_S3_BUCKET_NAME)"
	uv run python -m tools.use_s3 download $(AWS_S3_BUCKET_NAME) $(AWS_S3_PREFIX)/data.zip" $(LOCAL_DATA_PATH) 

# --- Pipelines ---

collect-notion-data-pipeline:
	uv run python -m tools.run --run-collect-notion-data-pipeline --no-cache

etl-pipeline:
	uv run python -m tools.run --run-etl-pipeline --no-cache

generate-dataset-pipeline:
	uv run python -m tools.run --run-generate-dataset-pipeline --no-cache

compute-rag-vector-index-pipeline:
	uv run python -m tools.run --run-compute-rag-vector-index-pipeline --no-cache

# --- Tests ---

test:
	uv run pytest tests/

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
