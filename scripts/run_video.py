"""Run the full MoveSense video pipeline on a real video file or image sequence.

Examples:
    python scripts/run_video.py --input data/real/teste.mp4 --max-frames 100
    python scripts/run_video.py --input data/MOT17-09/img1 --fps 30
"""

import argparse
import pathlib
import sys

# Garante import de train_classifier mesmo se executado fora da pasta scripts/
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from movesense.classifier import BehaviourClassifier
from movesense.detector import PedestrianDetector
from movesense.pipeline import run_video_pipeline
from movesense.tracker import SimpleTracker
from train_classifier import build_labeled_training_corpus


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run MoveSense detection, tracking, and behaviour classification on video."
    )
    parser.add_argument(
        "--input",
        type=pathlib.Path,
        default=pathlib.Path("data/synthetic/synthetic_video.avi"),
        help="Path to input video (.mp4/.avi) or MOT image directory (e.g. img1/).",
    )
    parser.add_argument(
        "--output-video",
        type=pathlib.Path,
        default=pathlib.Path("outputs_local/annotated_video.avi"),
        help="Path to save the annotated output video.",
    )
    parser.add_argument(
        "--output-csv",
        type=pathlib.Path,
        default=pathlib.Path("outputs_local/video_predictions.csv"),
        help="Path to save per-track behaviour predictions CSV.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="YOLO model weights path or name (default: yolov8n.pt).",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Detector confidence threshold (default: 0.25).",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=None,
        help="Override video FPS (auto-detected for video files, 25.0 for image folders).",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional limit on frames to process (useful for fast CPU testing).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"1. Loading YOLOv8 detector ({args.model}, conf={args.conf})...")
    detector = PedestrianDetector(model_name=args.model, conf_threshold=args.conf)

    print("2. Training Random Forest BehaviourClassifier...")
    clf = BehaviourClassifier(n_estimators=50, random_state=42)
    clf.train(build_labeled_training_corpus(seed=2026), target_col="label", test_size=0.25)

    tracker = SimpleTracker(iou_threshold=0.3, max_misses=5)

    print(f"3. Running end-to-end pipeline on: {args.input}")
    result = run_video_pipeline(
        input_path=args.input,
        output_video_path=args.output_video,
        output_csv_path=args.output_csv,
        detector=detector,
        tracker=tracker,
        classifier=clf,
        fps=args.fps,
        max_frames=args.max_frames,
    )

    preds = result["predictions_df"]
    print("\n" + "=" * 72)
    print(f"🎬 Frames processados: {result['frames_processed']} | Tracks: {result['total_tracks']}")
    print("=" * 72)
    if preds.empty:
        print("Nenhum pedestre detectado neste trecho.")
    else:
        for _, row in preds.iterrows():
            print(
                f"ID #{int(row['track_id']):<3} | "
                f"Frames: {int(row['duration_frames']):<4} | "
                f"Vel. Média: {row['mean_speed']:>6.1f} px/s | "
                f"Comportamento: [{str(row['predicted_behaviour']).upper()}]"
            )
    print("=" * 72)
    print(f"✅ Vídeo anotado salvo em: {args.output_video}")
    print(f"✅ Tabela CSV salva em  : {args.output_csv}")


if __name__ == "__main__":
    main()