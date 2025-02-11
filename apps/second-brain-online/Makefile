ifeq (,$(wildcard .env))
$(error .env file is missing. Please create one based on .env.example)
endif

include .env

export UV_PROJECT_ENVIRONMENT=.venv-online
export PYTHONPATH = .

# --- Default Values ---

CHECK_DIRS := .
RETRIEVER_CONFIG ?= configs/compute_rag_vector_index_openai_parent.yaml

# --- Utilities ---

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# --- Infrastructure --- 

local-docker-infrastructure-up:
	docker compose -f ../infrastructure/docker/docker-compose.yml up --build -d 

local-docker-infrastructure-stop:
	docker compose -f ../infrastructure/docker/docker-compose.yml stop

local-infrastructure-up: local-docker-infrastructure-up

local-infrastructure-stop: local-docker-infrastructure-stop


# --- Run ---

run_agent_app:
	uv run python -m tools.app --retriever-config-path=$(RETRIEVER_CONFIG) --ui

run_agent_query:
	uv run python -m tools.app --retriever-config-path=$(RETRIEVER_CONFIG) --query "What is the feature/training/inference (FTI) pipelines architecture?"

evaluate_agent:
	uv run python -m tools.evaluate_app --retriever-config-path=$(RETRIEVER_CONFIG)


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
