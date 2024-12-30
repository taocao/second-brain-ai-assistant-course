.PHONY: style check_code_quality

export PYTHONPATH = .
check_dirs := src

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
