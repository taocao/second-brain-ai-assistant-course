export PYTHONPATH = .
check_dirs := src

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# --- Infrastructure --- 

local-docker-infrastructure-up:
	docker compose up -d

local-docker-infrastructure-down:
	docker compose stop

local-zenml-server-down:
	uv run zenml logout --local

local-zenml-server-up:
ifeq ($(shell uname), Darwin)
	OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES uv run zenml login --local
else
	uv run zenml login --local
endif

local-infrastructure-up: local-docker-infrastructure-up local-zenml-server-down local-zenml-server-up

local-infrastructure-down: local-docker-infrastructure-down local-zenml-server-down

# --- Pipelines ---

collect-notion-pipeline:
	uv run python -m tools.run --run-collect-notion --no-cache

# --- Tests ---

test:
	uv run pytest tests/

# --- QA ---

format-fix:
	uv run ruff format $(check_dirs)
	uv run ruff check --select I --fix 

lint-fix:
	uv run ruff check --fix

format-check:
	uv run ruff format --check $(check_dirs) 
	uv run ruff check -e
	uv run ruff check --select I -e

lint-check:
	uv run ruff check $(check_dirs)
