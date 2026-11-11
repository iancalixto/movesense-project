"""Tests for MOT evaluation metrics (MOTA, Precision, Recall, ID Switches)."""

import pandas as pd
import pytest
from movesense.evaluation import evaluate_tracking


def test_evaluate_perfect_tracking():
    """Verify MOTA=1.0 and 0 ID switches when predictions match ground truth identically."""
    gt_df = pd.DataFrame({
        "frame": [1, 1, 2, 2],
        "id": [1, 2, 1, 2],
        "x": [100.0, 400.0, 105.0, 405.0],
        "y": [100.0, 200.0, 102.0, 202.0],
        "w": [50.0, 50.0, 50.0, 50.0],
        "h": [100.0, 100.0, 100.0, 100.0],
    })
    pred_df = gt_df.copy()

    metrics = evaluate_tracking(gt_df, pred_df, iou_threshold=0.5)

    assert metrics["mota"] == pytest.approx(1.0)
    assert metrics["precision"] == pytest.approx(1.0)
    assert metrics["recall"] == pytest.approx(1.0)
    assert metrics["id_switches"] == 0
    assert metrics["true_positives"] == 4


def test_evaluate_detects_id_switch():
    """Verify tracker evaluation counts an ID switch when predicted ID changes for same GT."""
    gt_df = pd.DataFrame({
        "frame": [1, 2],
        "id": [1, 1],
        "x": [100.0, 105.0],
        "y": [100.0, 102.0],
        "w": [50.0, 50.0],
        "h": [100.0, 100.0],
    })
    # No frame 1 o tracker chamou de ID 10; no frame 2 trocou para ID 20!
    pred_df = pd.DataFrame({
        "frame": [1, 2],
        "id": [10, 20],
        "x": [100.0, 105.0],
        "y": [100.0, 102.0],
        "w": [50.0, 50.0],
        "h": [100.0, 100.0],
    })

    metrics = evaluate_tracking(gt_df, pred_df, iou_threshold=0.5)

    assert metrics["id_switches"] == 1
    assert metrics["true_positives"] == 2
    assert metrics["mota"] == pytest.approx(0.5)  # 1 - (0 + 0 + 1)/2 = 0.5


def test_evaluate_counts_false_positives_and_misses():
    """Verify FP and FN (misses) reduce MOTA, precision, and recall properly."""
    gt_df = pd.DataFrame({
        "frame": [1, 1],
        "id": [1, 2],
        "x": [100.0, 500.0],
        "y": [100.0, 500.0],
        "w": [50.0, 50.0],
        "h": [100.0, 100.0],
    })
    # Frame 1: Achou o GT 1, perdeu o GT 2 (FN=1) e inventou um fantasma em (900, 900) (FP=1)
    pred_df = pd.DataFrame({
        "frame": [1, 1],
        "id": [1, 99],
        "x": [100.0, 900.0],
        "y": [100.0, 900.0],
        "w": [50.0, 50.0],
        "h": [100.0, 100.0],
    })

    metrics = evaluate_tracking(gt_df, pred_df, iou_threshold=0.5)

    assert metrics["true_positives"] == 1
    assert metrics["false_negatives"] == 1
    assert metrics["false_positives"] == 1
    assert metrics["precision"] == pytest.approx(0.5)
    assert metrics["recall"] == pytest.approx(0.5)
    assert metrics["mota"] == pytest.approx(0.0)  # 1 - (1 + 1 + 0)/2 = 0.0