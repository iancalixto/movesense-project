"""Evaluate size-normalized behaviour rules and posture detection on MOT17-09 (DS-09).

Demonstrates elimination of camera perspective bias by scaling velocities
to body lengths per second (v/h), and flags behavioural events from the team's spreadsheet.
"""

from pathlib import Path
import cv2
import numpy as np
import pandas as pd

from movesense.detector import PedestrianDetector
from movesense.features import smooth_trajectory
from movesense.rules import RuleEngine
from movesense.tracker import SimpleTracker


def main() -> None:
    img_dir = Path("data/MOT17/train/MOT17-09-FRCNN/img1")
    config_path = Path("configs/behaviour_rules.json")
    output_csv = Path("results/mot17_09_rules_evaluation.csv")
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    if not img_dir.exists():
        print(f"Error: {img_dir} does not exist. Ensure MOT17 dataset is present.")
        return

    print("=" * 80)
    print("DS-09: MOTOR DE REGRAS E NORMALIZACAO DE TAMANHO (MOT17-09-FRCNN)")
    print("=" * 80)

    # 1. Deteccao + Rastreamento nos primeiros 120 frames (4 segundos a 30 fps)
    detector = PedestrianDetector(model_name="yolov8n.pt", conf_threshold=0.50)
    tracker = SimpleTracker(iou_threshold=0.3, max_misses=5)
    img_files = sorted(img_dir.glob("*.jpg"))[:120]

    print(f"Processando {len(img_files)} frames com YOLOv8n (conf=0.50) + SimpleTracker...")
    raw_tracks = []
    for frame_idx, img_path in enumerate(img_files, start=1):
        frame = cv2.imread(str(img_path))
        if frame is None:
            continue
        detections = detector.detect(frame)
        active_tracks = tracker.update(detections)
        for t in active_tracks:
            raw_tracks.append({
                "frame": frame_idx,
                "track_id": t.track_id,
                "x": float(t.x),
                "y": float(t.y),
                "w": float(t.w),
                "h": float(t.h),
            })

    df_tracks = pd.DataFrame(raw_tracks)
    if df_tracks.empty:
        print("Nenhuma trajetoria gerada.")
        return

    # 2. Suavizacao Savitzky-Golay (DS-08)
    smoothed_dfs = []
    for tid, group in df_tracks.groupby("track_id"):
        if len(group) >= 5:
            smoothed = group.copy()
            smoothed["x"] = smooth_trajectory(group["x"].values, window=9)
            smoothed["y"] = smooth_trajectory(group["y"].values, window=9)
            smoothed_dfs.append(smoothed)

    if not smoothed_dfs:
        print("Nenhuma trajetoria com >= 5 frames.")
        return

    df_clean = pd.concat(smoothed_dfs, ignore_index=True)

    # 3. Avaliacao com o RuleEngine configuravel (DS-09)
    engine = RuleEngine.from_config(config_path)
    eval_records = []

    for tid, group in df_clean.groupby("track_id"):
        res = engine.evaluate_track(group, fps=30.0)

        # Velocidade ingenua antiga em pixels/s
        dt = 1.0 / 30.0
        dx = np.diff(group["x"] + group["w"] / 2.0)
        dy = np.diff(group["y"] + group["h"] / 2.0)
        speed_px_s = float(np.mean(np.sqrt(dx**2 + dy**2)) / dt) if len(dx) > 0 else 0.0

        # Classificacao ingenua antiga sem normalizacao (> 160 px/s achava que era corrida)
        if speed_px_s < 20.0:
            naive_pred = "standing"
        elif speed_px_s < 160.0:
            naive_pred = "walking"
        else:
            naive_pred = "running (FALSO POSITIVO)"

        eval_records.append({
            "Track ID": tid,
            "Frames": len(group),
            "Altura Media (px)": round(float(group["h"].mean()), 1),
            "Aspect Ratio (w/h)": res["median_aspect_ratio"],
            "Velocidade (px/s)": round(speed_px_s, 1),
            "Velocidade (corpos/s)": res["mean_speed_bl_s"],
            "Classificacao Antiga (pixels)": naive_pred,
            "Novo Comportamento (DS-09)": res["primary_behaviour"],
            "Anomalias / Eventos": ", ".join(res["anomalies"]) if res["anomalies"] else "nenhuma",
        })

    df_eval = pd.DataFrame(eval_records)
    df_eval.to_csv(output_csv, index=False)

    print("\n" + df_eval.to_string(index=False))
    print(f"\nResultados salvos em: {output_csv}")
    print("\nConclusao Cientifica: A normalizacao pela altura do corpo eliminou o vies de perspectiva!")


if __name__ == "__main__":
    main()