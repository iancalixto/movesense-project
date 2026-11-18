"""Run pedestrian detector on a video and save detections in MOT format.

Run:
    python scripts/run_detector.py
"""

import pathlib
import cv2
from tqdm import tqdm

from movesense.detector import PedestrianDetector


def main() -> None:
    video_path = pathlib.Path("data/synthetic/synthetic_video.avi")
    output_det_path = pathlib.Path("data/synthetic/detections_yolo.txt")

    if not video_path.exists():
        raise FileNotFoundError(
            f"Video not found at {video_path}. Run 'make step-04' first to render it!"
        )

    print(f"Loading YOLO detector (yolov8n.pt)...")
    detector = PedestrianDetector(model_name="yolov8n.pt", conf_threshold=0.25)

    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Processing video: {video_path} ({total_frames} frames)")

    output_det_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    frame_idx = 1
    with tqdm(total=total_frames, desc="Detecting pedestrians") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            detections = detector.detect(frame)
            for det in detections:
                # MOT detection format: frame, -1 (no ID yet), x, y, w, h, conf, -1, -1
                line = f"{frame_idx},-1,{det.x:.1f},{det.y:.1f},{det.w:.1f},{det.h:.1f},{det.conf:.2f},-1,-1"
                lines.append(line)

            frame_idx += 1
            pbar.update(1)

    cap.release()
    output_det_path.write_text("\n".join(lines) + "\n")
    print(f"\nDetection complete! Saved {len(lines)} detections to: {output_det_path}")


if __name__ == "__main__":
    main()