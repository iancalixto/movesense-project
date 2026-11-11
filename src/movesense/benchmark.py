"""Unified MOT17 + MOT20 benchmark governance, discovery, and regime-separated evaluation."""

import configparser
import pathlib
import cv2
import pandas as pd

from movesense.detector import PedestrianDetector
from movesense.evaluation import evaluate_tracking
from movesense.loader import load_mot_gt
from movesense.tracker import SimpleTracker

DETECTOR_SUFFIXES: tuple[str, ...] = ("-DPM", "-FRCNN", "-SDP")
IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".bmp"}


def canonical_sequence_id(sequence_name: str) -> str:
    """Return the underlying video sequence ID, stripping MOT17 detector suffixes."""
    for suffix in DETECTOR_SUFFIXES:
        if sequence_name.endswith(suffix):
            return sequence_name[: -len(suffix)]
    return sequence_name


def validate_no_sequence_leakage(
    train_seqs: list[str],
    eval_seqs: list[str],
) -> None:
    """Raise ValueError if train and eval splits share the same underlying video."""
    train_canonical = {canonical_sequence_id(name) for name in train_seqs}
    eval_canonical = {canonical_sequence_id(name) for name in eval_seqs}
    overlap = train_canonical.intersection(eval_canonical)
    if overlap:
        raise ValueError(
            f"Sequence split leakage detected for underlying video(s): {sorted(overlap)}"
        )


def _read_sequence_fps(seq_dir: pathlib.Path, default_fps: float = 25.0) -> float:
    ini_path = seq_dir / "seqinfo.ini"
    if not ini_path.exists():
        return default_fps
    cfg = configparser.ConfigParser()
    cfg.read(ini_path)
    return cfg.getfloat("Sequence", "frameRate", fallback=default_fps)


def _infer_dataset_name(sequence_name: str, fallback: str) -> str:
    if sequence_name.startswith("MOT17"):
        return "MOT17"
    if sequence_name.startswith("MOT20"):
        return "MOT20"
    return fallback


def discover_mot_sequences(
    root_dir: pathlib.Path | str,
    dataset_name: str | None = None,
    preferred_variant: str = "FRCNN",
) -> list[dict]:
    """Discover MOT sequences under root_dir while deduplicating detector variants."""
    root = pathlib.Path(root_dir)
    if not root.exists():
        return []

    selected: dict[str, dict] = {}
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if not (entry / "img1").is_dir() or not (entry / "gt" / "gt.txt").is_file():
            continue

        canon_id = canonical_sequence_id(entry.name)
        is_preferred = entry.name.endswith(f"-{preferred_variant}")
        if canon_id in selected and not is_preferred:
            continue

        selected[canon_id] = {
            "dataset": dataset_name or _infer_dataset_name(entry.name, fallback=root.name),
            "sequence": entry.name,
            "canonical_id": canon_id,
            "path": entry,
            "fps": _read_sequence_fps(entry),
        }

    return list(selected.values())


def evaluate_mot_sequence(
    seq_dir: pathlib.Path | str,
    dataset_name: str,
    detector: PedestrianDetector | None = None,
    tracker: SimpleTracker | None = None,
    max_frames: int | None = None,
    iou_threshold: float = 0.5,
    min_visibility: float = 0.0,
) -> dict:
    """Run detection + tracking on a single MOT17/MOT20 sequence and evaluate vs. GT."""
    seq_path = pathlib.Path(seq_dir)
    img_dir = seq_path / "img1"
    gt_path = seq_path / "gt" / "gt.txt"

    if not img_dir.is_dir() or not gt_path.is_file():
        raise FileNotFoundError(f"Invalid MOT sequence directory: {seq_path}")

    fps = _read_sequence_fps(seq_path)
    image_files = sorted(
        p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS
    )
    if max_frames is not None:
        image_files = image_files[:max_frames]

    gt_df = load_mot_gt(gt_path, min_visibility=min_visibility)
    gt_eval = gt_df[gt_df["frame"] <= len(image_files)].reset_index(drop=True)

    active_detector = detector if detector is not None else PedestrianDetector()
    active_tracker = tracker if tracker is not None else SimpleTracker(iou_threshold=0.3, max_misses=5)

    track_records: list[dict] = []
    for frame_idx, img_path in enumerate(image_files, start=1):
        frame = cv2.imread(str(img_path))
        if frame is None:
            continue
        detections = active_detector.detect(frame)
        active_tracks = active_tracker.update(detections)
        for track in active_tracks:
            track_records.append({
                "frame": frame_idx,
                "id": track.track_id,
                "x": track.x,
                "y": track.y,
                "w": track.w,
                "h": track.h,
                "conf": track.conf,
            })

    pred_df = (
        pd.DataFrame(track_records)
        if track_records
        else pd.DataFrame(columns=["frame", "id", "x", "y", "w", "h", "conf"])
    )

    metrics = evaluate_tracking(gt_eval, pred_df, iou_threshold=iou_threshold)
    return {
        "dataset": dataset_name,
        "sequence": seq_path.name,
        "canonical_id": canonical_sequence_id(seq_path.name),
        "fps": fps,
        "frames_evaluated": len(image_files),
        "gt_tracks": int(gt_eval["id"].nunique()) if not gt_eval.empty else 0,
        "pred_tracks": int(pred_df["id"].nunique()) if not pred_df.empty else 0,
        **metrics,
    }


def summarize_by_dataset(results_df: pd.DataFrame) -> pd.DataFrame:
    """Compute micro-averaged MOT metrics separately per dataset regime (MOT17 vs MOT20)."""
    if results_df.empty:
        return pd.DataFrame()

    rows: list[dict] = []
    for dataset_name, group in results_df.groupby("dataset", sort=True):
        tp = int(group["true_positives"].sum())
        fp = int(group["false_positives"].sum())
        fn = int(group["false_negatives"].sum())
        idsw = int(group["id_switches"].sum())
        total_gt = int(group["total_gt"].sum())
        frames = int(group["frames_evaluated"].sum())

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        mota = 1.0 - (fn + fp + idsw) / total_gt if total_gt > 0 else 0.0

        rows.append({
            "dataset": str(dataset_name),
            "sequences": len(group),
            "frames_evaluated": frames,
            "total_gt": total_gt,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "id_switches": idsw,
            "mota": float(mota),
            "precision": float(precision),
            "recall": float(recall),
        })

    return pd.DataFrame(rows)