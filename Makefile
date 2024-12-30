.PHONY: style check_code_quality

export PYTHONPATH = .
check_dirs := src

format:
	uv run ruff format  $(check_dirs)
	uv run ruff check --select I --fix 

lint:
	uv run ruff check --fix

check_code_quality:
	uv run ruff check $(check_dirs)
	# check sort
	uv run ruff check -e
	uv run ruff check --select I -e
