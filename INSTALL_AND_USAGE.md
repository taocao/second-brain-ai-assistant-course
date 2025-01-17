## Getting started

### Installation

To set it up and run

```bash
# uv venv
uv sync
```

### Development

You can install in `editable` mode the library

```bash
uv pip install -e .
```

You can now run, for example, a function defined as `scripts` in the [`pyproject.toml`](pyproject.toml)

```bash
make_me_laugh
```

### Infrastructure

```bash
make local-infrastructure-up
```


### Run ZenML pipelines

```bash
make collect-notion-pipeline
```

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