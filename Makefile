.PHONY: install test

install:
	uv pip install -e ".[dev]"

test:
	python -m pytest -q