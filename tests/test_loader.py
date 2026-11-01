"""Tests for standard MOT dataset loader."""

import pathlib
import tempfile
import pandas as pd
import pytest

from movesense.synthetic import generate_synthetic_mot
from movesense.loader import load_mot_file, MOT_COLUMNS


def test_load_mot_file_schema():
    """Verify load_mot_file returns a valid DataFrame with all standard MOT columns."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        gt_file = pathlib.Path(tmp_dir) / "gt.txt"
        generate_synthetic_mot(gt_file, n_pedestrians=3, n_frames=10, seed=2026)

        df = load_mot_file(gt_file)

        assert isinstance(df, pd.DataFrame), "Output must be a pandas DataFrame"
        assert list(df.columns) == MOT_COLUMNS, f"Columns must match standard MOT schema: {MOT_COLUMNS}"
        assert len(df) == 30, f"Expected 30 rows (3 pedestrians x 10 frames), got {len(df)}"
        assert df["frame"].dtype.kind in "iu", "frame column must be integer"
        assert df["id"].dtype.kind in "iu", "id column must be integer"


def test_load_mot_file_not_found():
    """Verify load_mot_file raises FileNotFoundError for missing paths."""
    with pytest.raises(FileNotFoundError):
        load_mot_file(pathlib.Path("non_existent_gt.txt"))