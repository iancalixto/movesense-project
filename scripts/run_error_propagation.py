"""Run end-to-end error propagation experiment (Detector -> Tracker -> Features -> Classifier).

Run:
    python scripts/run_error_propagation.py
"""

import pathlib
from collections import defaultdict
import numpy as np
import pandas as pd

from movesense.classifier import BehaviourClassifier
from movesense.detector import Detection
from movesense.evaluation import evaluate_tracking
from movesense.features import extract_trajectory_features
from movesense.loader import load_mot_file
from movesense.tracker import SimpleTracker
from train_classifier import build_labeled_training_corpus


def simulate_noisy_detections(
    gt_df: pd.DataFrame,
    dropout_rate: float,
    jitter_px: float,
    seed: int = 2026,
) -> dict[int, list[Detection]]:
    """Degrade ground-truth boxes to simulate imperfect real-world detectors."""
    rng = np.random.default_rng(seed)
    frames_det: dict[int, list[Detection]] = defaultdict(list)

    for _, row in gt_df.iterrows():
        # Simula False Negative (detector piscou e perdeu o pedestre neste frame)
        if rng.random() < dropout_rate:
            continue

        dx = float(rng.normal(0.0, jitter_px)) if jitter_px > 0 else 0.0
        dy = float(rng.normal(0.0, jitter_px)) if jitter_px > 0 else 0.0

        det = Detection(
            x=max(0.0, float(row["x"]) + dx),
            y=max(0.0, float(row["y"]) + dy),
            w=float(row["w"]),
            h=float(row["h"]),
            conf=float(np.clip(1.0 - dropout_rate * 0.5, 0.3, 1.0)),
        )
        frames_det[int(row["frame"])].append(det)

    return frames_det


def main() -> None:
    gt_path = pathlib.Path("data/synthetic/gt.txt")
    results_path = pathlib.Path("results/error_propagation_summary.csv")

    if not gt_path.exists():
        raise FileNotFoundError(f"Ground truth missing at {gt_path}. Run 'make step-02' first!")

    gt_df = load_mot_file(gt_path)
    total_frames = int(gt_df["frame"].max())

    # Treina nosso classificador padrão para testar impacto no comportamento
    clf = BehaviourClassifier(n_estimators=50, random_state=42)
    clf.train(build_labeled_training_corpus(seed=2026), target_col="label", test_size=0.25)

    scenarios = [
        ("1. Ideal (Baseline)", 0.00, 0.0),
        ("2. Ruído Leve (Edge)", 0.05, 5.0),
        ("3. Oclusão Moderada", 0.20, 15.0),
        ("4. Detector Degradado", 0.40, 25.0),
    ]

    summary_rows = []
    print("\n" + "=" * 102)
    print("🔬 EXPERIMENTO DE PROPAGAÇÃO DE ERROS: Sem Suavização (Raw) vs. Com Suavização (DS-08)")
    print("=" * 102)
    print(
        f"{'Cenário':<23} | {'MOTA':>7} | {'Recall':>7} | {'IDSW':>5} | "
        f"{'Tracks':>6} | {'Walk(Raw)':>9} | {'Walk(DS08)':>10}"
    )
    print("-" * 102)

    for name, drop, jitter in scenarios:
        noisy_dets = simulate_noisy_detections(gt_df, dropout_rate=drop, jitter_px=jitter)
        tracker = SimpleTracker(iou_threshold=0.3, max_misses=3)

        track_records = []
        for f in range(1, total_frames + 1):
            active_tracks = tracker.update(noisy_dets.get(f, []))
            for t in active_tracks:
                track_records.append({
                    "frame": f,
                    "id": t.track_id,
                    "x": t.x,
                    "y": t.y,
                    "w": t.w,
                    "h": t.h,
                    "conf": t.conf,
                })

        pred_df = pd.DataFrame(track_records)
        eval_metrics = evaluate_tracking(gt_df, pred_df, iou_threshold=0.5)

        # Sem suavização (Raw)
        feat_raw = extract_trajectory_features(pred_df, fps=25, smooth_window=1, min_frames=1)
        preds_raw = clf.predict(feat_raw) if not feat_raw.empty else []
        walk_raw_pct = (preds_raw.count("walking") / len(preds_raw) * 100.0) if preds_raw else 0.0

        # Com suavização Savitzky-Golay + filtro de micro-tracks (DS-08)
        feat_smooth = extract_trajectory_features(pred_df, fps=25, smooth_window=9, min_frames=5)
        preds_smooth = clf.predict(feat_smooth) if not feat_smooth.empty else []
        walk_smooth_pct = (preds_smooth.count("walking") / len(preds_smooth) * 100.0) if preds_smooth else 0.0

        print(
            f"{name:<23} | "
            f"{eval_metrics['mota']*100:>6.1f}% | "
            f"{eval_metrics['recall']*100:>6.1f}% | "
            f"{eval_metrics['id_switches']:>5d} | "
            f"{len(feat_raw):>6d} | "
            f"{walk_raw_pct:>8.1f}% | "
            f"{walk_smooth_pct:>9.1f}%"
        )

        summary_rows.append({
            "scenario": name,
            "dropout_rate": drop,
            "jitter_px": jitter,
            "mota": eval_metrics["mota"],
            "precision": eval_metrics["precision"],
            "recall": eval_metrics["recall"],
            "id_switches": eval_metrics["id_switches"],
            "total_predicted_tracks": len(feat_raw),
            "walking_accuracy_pct": walk_raw_pct,
            "walking_accuracy_smoothed_pct": walk_smooth_pct,
        })

    results_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary_rows).to_csv(results_path, index=False)
    print("=" * 102)
    print(f"✅ Relatório experimental salvo em: {results_path}\n")


if __name__ == "__main__":
    main()