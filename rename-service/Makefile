.DEFAULT_GOAL := help
PROJECT_DIR := rename/

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[35m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install:  ## Install the python module to the current environment
	python -m pip install -e .

.PHONY: install_dev
install_dev:  ## Install the python module with dev dependencies
	python -m pip install -e ".[dev]"

.PHONY: precommit_install
precommit_install:  ## Install the project's precommit hooks from .pre-commit-config.yaml
	@echo "Installing pre-commit hooks"
	@echo "Make sure to first run install_dev first"
	pre-commit install

.PHONY: py_format
py_format:  ## Run black and isort to format the Python codebase
	pycln $(PROJECT_DIR)
	isort $(PROJECT_DIR) --profile black --multi-line 3
	black $(PROJECT_DIR)
