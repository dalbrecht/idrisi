.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help bootstrap dev test lint lint-fix fmt build serve build-web run ls sync-standards

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

bootstrap: ## Create venv and install all deps
	uv venv
	uv pip install -e ".[dev]"

dev: ## Install in editable mode with dev extras
	uv pip install -e ".[dev]"

test: ## Run pytest
	uv run pytest

lint: ## Run ruff check and mypy
	uv run ruff check src tests
	uv run mypy src

lint-fix: ## Auto-fix ruff lint issues
	uv run ruff check --fix src tests

fmt: ## Format code with ruff
	uv run ruff format src tests

build: ## Build wheel
	uv run python -m build

serve: ## Start the FastAPI dev server
	uv run uvicorn voyages.server.app:create_app --factory --reload

build-web: ## Build the Svelte front-end
	cd web && npm run build

run: ## Run the CLI
	uv run voyages

ls: ## List all make targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sed 's/:.*//' | sort

sync-standards: ## Sync coding-standards submodule to latest
	git submodule update --init --remote .standards
