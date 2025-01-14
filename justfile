# Default target executed when no arguments are given.
[private]
default:
  @just --list

install:
    uv sync
    uv run pre-commit install

test *args:
	uv run pytest {{args}}

lint:
	uv run pre-commit run ruff --files
	uv run pre-commit run ruff-format --files

docs:
    uv run sphinx-build -T -b html docs docs/_build

typing:
    uv run mypy --install-types --non-interactive .
