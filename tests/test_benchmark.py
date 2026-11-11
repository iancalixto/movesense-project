"""Contract tests for unified MOT17 + MOT20 benchmark governance and evaluation (DE-07)."""

import cv2
import numpy as np
import pandas as pd
import pytest

from movesense.benchmark import (
    canonical_sequence_id,
    discover_mot_sequences,
    evaluate_mot_sequence,
    summarize_by_dataset,
    validate_no_sequence_leakage,
)
from movesense.detector import Detection
from movesense.tracker import SimpleTracker


def test_canonical_sequence_id_strips_mot17_detector_suffix():
    assert canonical_sequence_id("MOT17-09-FRCNN") == "MOT17-09"
    assert canonical_sequence_id("MOT17-09-SDP") == "MOT17-09"
    assert canonical_sequence_id("MOT17-09-DPM") == "MOT17-09"
    assert canonical_sequence_id("MOT20-01") == "MOT20-01"


def test_validate_no_sequence_leakage_blocks_duplicate_underlying_video():
    with pytest.raises(ValueError, match="leakage"):
        validate_no_sequence_leakage(
            train_seqs=["MOT17-02-FRCNN", "MOT17-09-FRCNN"],
            eval_seqs=["MOT17-04-FRCNN", "MOT17-09-SDP"],
        )

    validate_no_sequence_leakage(
        train_seqs=["MOT17-02-FRCNN", "MOT17-09-FRCNN"],
        eval_seqs=["MOT17-04-FRCNN", "MOT20-01"],
    )


def test_discover_mot_sequences_deduplicates_mot17_and_reads_mot20(tmp_path):
    for name in ["MOT17-09-DPM", "MOT17-09-FRCNN", "MOT20-01"]:
        seq = tmp_path / name
        (seq / "img1").mkdir(parents=True)
        (seq / "gt").mkdir(parents=True)
        (seq / "gt" / "gt.txt").write_text("1,1,10,10,20,40,1,1,1\n")

    found = discover_mot_sequences(tmp_path, preferred_variant="FRCNN")
    names = [item["sequence"] for item in found]

    assert "MOT17-09-FRCNN" in names
    assert "MOT17-09-DPM" not in names
    assert "MOT20-01" in names


def test_evaluate_mot_sequence_and_summarize_by_dataset_keep_regimes_separate(tmp_path):
    class _SingleBoxDetector:
        def detect(self, frame: np.ndarray) -> list[Detection]:
            return [Detection(x=20.0, y=30.0, w=40.0, h=80.0, conf=0.95)]

    seq_dir = tmp_path / "MOT20-01"
    (seq_dir / "img1").mkdir(parents=True)
    (seq_dir / "gt").mkdir(parents=True)
    (seq_dir / "seqinfo.ini").write_text("[Sequence]\nname=MOT20-01\nframeRate=25\n")
    (seq_dir / "gt" / "gt.txt").write_text(
        "1,1,20,30,40,80,1,1,1.0\n"
        "2,1,20,30,40,80,1,1,1.0\n"
        "2,9,90,90,30,60,0,12,1.0\n"
    )

    dummy_img = np.zeros((160, 160, 3), dtype=np.uint8)
    cv2.imwrite(str(seq_dir / "img1" / "000001.jpg"), dummy_img)
    cv2.imwrite(str(seq_dir / "img1" / "000002.jpg"), dummy_img)

    row = evaluate_mot_sequence(
        seq_dir=seq_dir,
        dataset_name="MOT20",
        detector=_SingleBoxDetector(),
        tracker=SimpleTracker(iou_threshold=0.3, max_misses=3),
    )

    assert row["dataset"] == "MOT20"
    assert row["sequence"] == "MOT20-01"
    assert row["mota"] == pytest.approx(1.0)
    assert row["id_switches"] == 0

    df = pd.DataFrame([
        row,
        {
            "dataset": "MOT17",
            "sequence": "MOT17-09-FRCNN",
            "frames_evaluated": 2,
            "true_positives": 4,
            "false_positives": 1,
            "false_negatives": 1,
            "id_switches": 0,
            "total_gt": 5,
            "mota": 0.6,
            "precision": 0.8,
            "recall": 0.8,
        },
    ])
    summary = summarize_by_dataset(df)
    assert set(summary["dataset"]) == {"MOT17", "MOT20"}
    mot17_mota = float(summary.loc[summary["dataset"] == "MOT17", "mota"].iloc[0])
    mot20_mota = float(summary.loc[summary["dataset"] == "MOT20", "mota"].iloc[0])
    assert mot17_mota == pytest.approx(0.6)
    assert mot20_mota == pytest.approx(1.0)