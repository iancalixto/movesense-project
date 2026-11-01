"""Contract tests for the synthetic MOT ground-truth generator."""

import pathlib
import tempfile

from movesense.synthetic import generate_synthetic_mot


def test_generate_creates_file():
    """Verify that generate_synthetic_mot creates a gt.txt file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = pathlib.Path(tmp_dir) / "gt.txt"
        generate_synthetic_mot(output_file, n_pedestrians=3, n_frames=10, seed=2026)
        assert output_file.exists(), "gt.txt was not created"


def test_mot_format_nine_columns():
    """Verify that each line in gt.txt contains exactly 9 comma-separated fields."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = pathlib.Path(tmp_dir) / "gt.txt"
        generate_synthetic_mot(output_file, n_pedestrians=3, n_frames=10, seed=2026)
        lines = output_file.read_text().strip().splitlines()

        assert len(lines) > 0, "gt.txt is empty"
        for i, line in enumerate(lines):
            fields = line.split(",")
            assert len(fields) == 9, f"Line {i} has {len(fields)} fields, expected 9"