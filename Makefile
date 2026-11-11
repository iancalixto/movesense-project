.PHONY: install test step-02 step-04 step-05 step-06 step-07 step-08 step-09

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

step-06:
	python scripts/run_detector.py

step-07:
	python scripts/run_tracker.py

step-08:
	python scripts/extract_features.py

step-09:
	python scripts/train_classifier.py

step-10:
	python scripts/run_error_propagation.py