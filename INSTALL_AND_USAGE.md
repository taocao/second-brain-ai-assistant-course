## Getting started

### Installation

To set it up and run

```bash
uv venv
uv sync
```
Then

```bash
python main.py
```

Will output a random joke

```
Why did the cow in the pasture get promoted at work? ...  Because he is OUT-STANDING in his field!
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

### Linting

```
ruff check
```


### Formatting

```
ruff format
```

## CI/CD

### Tests
Tests inside `/tests` are run using [`pytest`](https://docs.pytest.org/en/stable/) on PR both on `dev` and `main`