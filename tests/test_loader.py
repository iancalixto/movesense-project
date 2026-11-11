"""Tests for standard MOT dataset loader."""

import pathlib
import tempfile
import pandas as pd
import pytest

from movesense.synthetic import generate_synthetic_mot
from movesense.loader import load_mot_file, load_mot_gt, MOT_COLUMNS


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


def test_load_mot_gt_filters_ignore_and_non_pedestrian_classes(tmp_path):
    """Verify load_mot_gt keeps only active pedestrian annotations by default."""
    gt_file = tmp_path / "gt.txt"
    gt_file.write_text(
        "1,1,100,100,50,120,1,1,0.95\n"   # Válido (flag=1, class_id=1, vis=0.95)
        "1,2,200,100,50,120,0,1,0.80\n"   # Ignorado (flag=0)
        "1,3,300,100,50,120,1,7,1.00\n"   # Não-pedestre (class_id=7 static person)
        "1,4,400,100,50,120,1,12,1.00\n"  # Não-pedestre (class_id=12 distractor)
        "2,1,105,100,50,120,1,1,0.15\n"   # Válido, mas visibilidade baixa (0.15)
    )

    filtered = load_mot_gt(gt_file)
    assert len(filtered) == 2
    assert list(filtered["id"]) == [1, 1]

    strict_vis = load_mot_gt(gt_file, min_visibility=0.5)
    assert len(strict_vis) == 1
    assert strict_vis.iloc[0]["frame"] == 1