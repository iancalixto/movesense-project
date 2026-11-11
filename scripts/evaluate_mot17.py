"""Evaluate MoveSense YOLOv8 + SimpleTracker baseline on a real MOT17 sequence.

Examples:
    python scripts/evaluate_mot17.py
    python scripts/evaluate_mot17.py --seq-dir data/MOT17/train/MOT17-09-FRCNN --max-frames 120
"""

import argparse
import configparser
import pathlib
import cv2
import pandas as pd

from movesense.detector import PedestrianDetector
from movesense.evaluation import evaluate_tracking
from movesense.loader import load_mot_gt
from movesense.tracker import SimpleTracker

IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".bmp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate MoveSense detector + tracker against real MOT17 ground truth."
    )
    parser.add_argument(
        "--seq-dir",
        type=pathlib.Path,
        default=pathlib.Path("data/MOT17/train/MOT17-09-FRCNN"),
        help="Path to MOT sequence folder containing img1/, gt/gt.txt, and seqinfo.ini.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=120,
        help="Number of initial frames to evaluate (default: 120 for fast CPU baseline).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="YOLO weights path or model name (default: yolov8n.pt).",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Detector confidence threshold (default: 0.25).",
    )
    parser.add_argument(
        "--iou-thresh",
        type=float,
        default=0.5,
        help="IoU threshold for matching predictions to GT boxes (default: 0.5).",
    )
    parser.add_argument(
        "--min-vis",
        type=float,
        default=0.0,
        help="Minimum visibility ratio for GT boxes (default: 0.0).",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("results/mot17_baseline_eval.csv"),
        help="Path to save evaluation metrics CSV.",
    )
    return parser.parse_args()


def _read_sequence_fps(seq_dir: pathlib.Path, default_fps: float = 25.0) -> float:
    ini_path = seq_dir / "seqinfo.ini"
    if not ini_path.exists():
        return default_fps
    cfg = configparser.ConfigParser()
    cfg.read(ini_path)
    return cfg.getfloat("Sequence", "frameRate", fallback=default_fps)


def main() -> None:
    args = parse_args()
    img_dir = args.seq_dir / "img1"
    gt_path = args.seq_dir / "gt" / "gt.txt"

    if not img_dir.exists() or not gt_path.exists():
        raise FileNotFoundError(
            f"Expected img1/ and gt/gt.txt inside MOT sequence directory: {args.seq_dir}"
        )

    fps = _read_sequence_fps(args.seq_dir)
    image_files = sorted(
        p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS
    )
    if args.max_frames is not None:
        image_files = image_files[: args.max_frames]

    print(f"1. Loading filtered MOT17 GT from: {gt_path} (min_vis={args.min_vis})")
    gt_df = load_mot_gt(gt_path, min_visibility=args.min_vis)
    gt_eval = gt_df[gt_df["frame"] <= len(image_files)].reset_index(drop=True)

    print(f"2. Running {args.model} + SimpleTracker on {len(image_files)} frames ({fps:.0f} FPS)...")
    detector = PedestrianDetector(model_name=args.model, conf_threshold=args.conf)
    tracker = SimpleTracker(iou_threshold=0.3, max_misses=5)

    track_records: list[dict] = []
    for frame_idx, img_path in enumerate(image_files, start=1):
        frame = cv2.imread(str(img_path))
        if frame is None:
            continue
        detections = detector.detect(frame)
        active_tracks = tracker.update(detections)
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

    metrics = evaluate_tracking(gt_eval, pred_df, iou_threshold=args.iou_thresh)
    n_pred_tracks = int(pred_df["id"].nunique()) if not pred_df.empty else 0
    n_gt_tracks = int(gt_eval["id"].nunique()) if not gt_eval.empty else 0

    print("\n" + "=" * 72)
    print(f"📊 AVALIAÇÃO REAL MOT17 ({args.seq_dir.name} | {len(image_files)} frames)")
    print("=" * 72)
    print(f"MOTA            : {metrics['mota']*100:.1f}%")
    print(f"Precision       : {metrics['precision']*100:.1f}%")
    print(f"Recall          : {metrics['recall']*100:.1f}%")
    print(f"True Positives  : {metrics['true_positives']} / {metrics['total_gt']} GT boxes")
    print(f"False Positives : {metrics['false_positives']}")
    print(f"False Negatives : {metrics['false_negatives']}")
    print(f"ID Switches     : {metrics['id_switches']}")
    print(f"Tracks Preditos : {n_pred_tracks} (vs {n_gt_tracks} IDs reais no GT)")
    print("=" * 72)

    summary = pd.DataFrame([{
        "sequence": args.seq_dir.name,
        "frames_evaluated": len(image_files),
        "fps": fps,
        "model": args.model,
        "conf_threshold": args.conf,
        "iou_threshold": args.iou_thresh,
        "min_visibility": args.min_vis,
        "gt_tracks": n_gt_tracks,
        "pred_tracks": n_pred_tracks,
        **metrics,
    }])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index=False)
    print(f"✅ Relatório salvo em: {args.output}")


if __name__ == "__main__":
    main()