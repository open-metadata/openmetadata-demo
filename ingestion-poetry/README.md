# OpenMetadata Ingestion with Poetry

Setting up the ingestion dependencies using [poetry](https://python-poetry.org/).

## Install Poetry

1. Install poetry with the [docs](https://python-poetry.org/docs/): `curl -sSL https://install.python-poetry.org | python3 -`
2. Export the path, e.g., `export PATH="/Users/pmbrull/.local/bin:$PATH"`
3. Validate with `poetry --version`

## Project Setup

1. `poetry new poetry-demo`. This is what created the `poetry-demo` directory here.
2. `openmetadata-ingestion` supports Python 3.7, 3.8 and 3.9, so we update the default `pyproject.toml` to reflect it,
   as well as adding the `openmetadata-ingestion` dependencies.
    ```toml
    [tool.poetry.dependencies]
    python = "^3.7.1,<3.10"
    commonregex = "1.5.3"
    openmetadata-ingestion = { version = "0.13.1.2", extras = ["bigquery"] }
    ```
3. Note how we also needed to flag `commonregex`. `poetry` was not properly installing it from the ingestion dependencies
4. Install the project with `poetry install`.

Finally, validate the installation via:

```
❯ which python
/Users/pmbrull/Library/Caches/pypoetry/virtualenvs/poetry-demo-Q8tmXXm6-py3.9/bin/python
❯ python -m metadata --version
metadata 0.13.1.2 from /Users/pmbrull/Library/Caches/pypoetry/virtualenvs/poetry-demo-Q8tmXXm6-py3.9/lib/python3.9 (python 3.9)
```
