docs_build := "docs/_build"
sphinx_opts:= "-d " + docs_build + "/doctrees docs"

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
	uv run pre-commit run --hook-stage manual --all-files

docs:
    uv run sphinx-build -T -b html {{sphinx_opts}} {{docs_build}}

doctest:
    uv run python -m doctest -v examples/wiki/wiki.py
    uv run sphinx-build -E -b doctest {{sphinx_opts}} {{docs_build}}/doctest
    uv run sphinx-build -b linkcheck {{sphinx_opts}} {{docs_build}}/linkcheck

typing:
    uv run mypy --install-types --non-interactive .
