.PHONY: install test step-02

install:
	uv pip install -e ".[dev]"

test:
	python -m pytest -q

step-02:
	python scripts/generate_synthetic.py