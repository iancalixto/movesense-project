"""Run pedestrian tracker on video detections and export MOT tracks.

Run:
    python scripts/run_tracker.py
"""

import pathlib
from collections import defaultdict
from tqdm import tqdm

from movesense.detector import Detection
from movesense.loader import load_mot_file
from movesense.tracker import SimpleTracker


def main() -> None:
    gt_path = pathlib.Path("data/synthetic/gt.txt")
    output_tracks_path = pathlib.Path("data/synthetic/tracks.txt")

    if not gt_path.exists():
        raise FileNotFoundError(
            f"Ground-truth not found at {gt_path}. Run 'make step-02' first!"
        )

    print("Loading detections / ground-truth for tracking...")
    df = load_mot_file(gt_path)

    # Agrupa as caixas por frame
    frames_data: dict[int, list[Detection]] = defaultdict(list)
    for _, row in df.iterrows():
        f = int(row["frame"])
        det = Detection(
            x=float(row["x"]),
            y=float(row["y"]),
            w=float(row["w"]),
            h=float(row["h"]),
            conf=float(row["conf"]),
        )
        frames_data[f].append(det)

    total_frames = max(frames_data.keys()) if frames_data else 0
    print(f"Tracking across {total_frames} frames using SimpleTracker (IoU)...")

    tracker = SimpleTracker(iou_threshold=0.3, max_misses=3)
    output_lines: list[str] = []
    unique_track_ids: set[int] = set()

    with tqdm(total=total_frames, desc="Tracking pedestrians") as pbar:
        for f in range(1, total_frames + 1):
            detections_in_frame = frames_data.get(f, [])
            active_tracks = tracker.update(detections_in_frame)

            for t in active_tracks:
                unique_track_ids.add(t.track_id)
                # Formato oficial MOTChallenge para rastreamento:
                # frame, track_id, bb_left, bb_top, bb_width, bb_height, conf, -1, -1, -1
                line = f"{f},{t.track_id},{t.x:.1f},{t.y:.1f},{t.w:.1f},{t.h:.1f},{t.conf:.2f},-1,-1,-1"
                output_lines.append(line)

            pbar.update(1)

    output_tracks_path.parent.mkdir(parents=True, exist_ok=True)
    output_tracks_path.write_text("\n".join(output_lines) + "\n")

    print(f"\nTracking complete!")
    print(f"Total de frames processados: {total_frames}")
    print(f"Pedestres únicos identificados: {len(unique_track_ids)} (IDs: {sorted(unique_track_ids)})")
    print(f"Arquivo de trajetórias salvo em: {output_tracks_path}")


if __name__ == "__main__":
    main()