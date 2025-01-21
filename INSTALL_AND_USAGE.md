# Getting started

## Installation

To set it up and run

```bash
# uv venv
# uv sync
uv pip install -e .
. ./.venv/bin/activate
```

Crew4AI:
```bash
# Run post-installation setup
crawl4ai-setup

# Verify your installation
crawl4ai-doctor
```

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

## Development

You can install in `editable` mode the library

```bash
uv pip install -e .
```


## Infrastructure

```bash
make local-infrastructure-up
```

## Running the ML pipelines / Lessons

## Optional - Collect custom Notion data
```bash
make collect-notion-pipeline
```

### Lesson 1

NO CODE


### Lesson 2: Populate MongoDB NoSQL and vector database

```bash
make download-raw-dataset
make etl-pipeline
make compute-rag-vector-index-pipeline
```

Or if you have issues with crawling, you can use our pre-computed dataset to populate MongoDB:
```bash
make download-crawled-dataset
make etl-precomputed-pipeline
make compute-rag-vector-index-pipeline
```

## Utility commands

### Formatting

```
make format-check
make format-fix
```

### Linting

```bash
make lint-check
make lint-fix
```

### Tests

```bash
make test
```

## Others

### Notion

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