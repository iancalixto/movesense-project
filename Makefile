.PHONY: install test step-02 step-04 step-05

install:
	uv pip install -e ".[dev]"

test:
	python -m pytest -q

step-02:
	python scripts/generate_synthetic.py

step-04:
	python scripts/render_video.py

step-05:
	python scripts/inspect_dataset.py