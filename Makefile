export PYTHONPATH = .
check_dirs := src

# --- Infrastructure --- 

local-docker-infrastructure-up:
	docker compose up -d

local-docker-infrastructure-down:
	docker compose stop

local-zenml-server-down:
	uv run zenml down

local-zenml-server-up:
ifeq ($(shell uname), Darwin)
	OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES uv run zenml up
else
	uv run zenml up
endif

local-infrastructure-up: local-docker-infrastructure-up local-zenml-server-down local-zenml-server-up

local-infrastructure-down: local-docker-infrastructure-down local-zenml-server-down

# --- Pipelines ---

collect-notion-pipeline:
	uv run python -m tools.run --run-collect-notion

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
