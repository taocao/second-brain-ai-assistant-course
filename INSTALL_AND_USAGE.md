# Getting started

## Installation

To set it up and run

```bash
# uv venv
uv sync
```

## Development

You can install in `editable` mode the library

```bash
uv pip install -e .
```


## Infrastructure

```bash
make local-infrastructure-up
```


## Run ZenML pipelines

### Notion (optionl)
```bash
make collect-notion-pipeline
```

### Populate MongoDB vector index

```bash
make download-raw-dataset
# Validate using test: make test-download-raw-dataset
make etl-pipeline
# Validate using test: make test-etl-pipeline
make compute-rag-vector-index-pipeline
# Validate using test: make test-rag-vector-index-pipeline
```

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

## Notion

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