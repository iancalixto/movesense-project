"""Contract tests for the end-to-end video pipeline (DS-06)."""

import cv2
import numpy as np
import pandas as pd

from movesense.classifier import BehaviourClassifier
from movesense.detector import Detection
from movesense.pipeline import run_video_pipeline
from movesense.tracker import SimpleTracker


class _FakeDetector:
    """Deterministic lightweight detector simulating a realistic walking pedestrian."""

    def __init__(self) -> None:
        self.frame_idx = 0

    def detect(self, frame: np.ndarray) -> list[Detection]:
        self.frame_idx += 1
        # Caminha 35 frames (~177 px totais) com variação natural do passo (4.4 a 6.0 px/frame)
        step_jitter = 0.8 if self.frame_idx % 2 == 0 else 0.0
        x = 20.0 + (self.frame_idx - 1) * 5.2 + step_jitter
        return [Detection(x=x, y=100.0, w=40.0, h=100.0, conf=0.95)]


def _make_trained_classifier() -> BehaviourClassifier:
    train_df = pd.DataFrame([
        {"duration_frames": 20, "mean_speed": 2.0, "max_speed": 5.0, "std_speed": 1.0, "mean_acceleration": 0.0, "confinement_radius": 3.0, "label": "standing"},
        {"duration_frames": 25, "mean_speed": 4.0, "max_speed": 7.0, "std_speed": 1.5, "mean_acceleration": 0.1, "confinement_radius": 5.0, "label": "standing"},
        {"duration_frames": 30, "mean_speed": 3.0, "max_speed": 6.0, "std_speed": 1.0, "mean_acceleration": -0.1, "confinement_radius": 4.0, "label": "standing"},
        {"duration_frames": 35, "mean_speed": 5.0, "max_speed": 8.0, "std_speed": 2.0, "mean_acceleration": 0.0, "confinement_radius": 6.0, "label": "standing"},
        {"duration_frames": 20, "mean_speed": 120.0, "max_speed": 150.0, "std_speed": 10.0, "mean_acceleration": 0.0, "confinement_radius": 180.0, "label": "walking"},
        {"duration_frames": 25, "mean_speed": 130.0, "max_speed": 160.0, "std_speed": 12.0, "mean_acceleration": 1.0, "confinement_radius": 200.0, "label": "walking"},
        {"duration_frames": 30, "mean_speed": 110.0, "max_speed": 140.0, "std_speed": 9.0, "mean_acceleration": -1.0, "confinement_radius": 170.0, "label": "walking"},
        {"duration_frames": 35, "mean_speed": 125.0, "max_speed": 155.0, "std_speed": 11.0, "mean_acceleration": 0.5, "confinement_radius": 190.0, "label": "walking"},
    ])
    clf = BehaviourClassifier(n_estimators=20, random_state=42)
    clf.train(train_df, target_col="label", test_size=0.25)
    return clf


def test_run_video_pipeline_processes_video_and_saves_outputs(tmp_path):
    input_video = tmp_path / "sample.avi"
    output_video = tmp_path / "annotated.avi"
    output_csv = tmp_path / "predictions.csv"

    # Cria um mini-vídeo sintético válido de 35 frames (320x240 @ 25 FPS)
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(str(input_video), fourcc, 25.0, (320, 240))
    for _ in range(35):
        writer.write(np.zeros((240, 320, 3), dtype=np.uint8))
    writer.release()

    result = run_video_pipeline(
        input_path=input_video,
        output_video_path=output_video,
        output_csv_path=output_csv,
        detector=_FakeDetector(),
        tracker=SimpleTracker(iou_threshold=0.3, max_misses=3),
        classifier=_make_trained_classifier(),
    )

    assert output_video.exists() and output_video.stat().st_size > 0
    assert output_csv.exists()
    assert result["frames_processed"] == 35
    assert result["total_tracks"] == 1
    assert result["predictions_df"].iloc[0]["predicted_behaviour"] == "walking"


def test_run_video_pipeline_handles_empty_detections(tmp_path):
    class _EmptyDetector:
        def detect(self, frame: np.ndarray) -> list[Detection]:
            return []

    input_video = tmp_path / "empty.avi"
    output_video = tmp_path / "empty_out.avi"
    output_csv = tmp_path / "empty_preds.csv"

    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(str(input_video), fourcc, 25.0, (320, 240))
    for _ in range(5):
        writer.write(np.zeros((240, 320, 3), dtype=np.uint8))
    writer.release()

    result = run_video_pipeline(
        input_path=input_video,
        output_video_path=output_video,
        output_csv_path=output_csv,
        detector=_EmptyDetector(),
        tracker=SimpleTracker(),
        classifier=_make_trained_classifier(),
    )

    assert output_video.exists()
    assert output_csv.exists()
    assert result["frames_processed"] == 5
    assert result["total_tracks"] == 0
    assert result["predictions_df"].empty