"""End-to-end pedestrian detection, tracking, and behaviour video pipeline."""

from collections.abc import Iterator
import pathlib
import cv2
import numpy as np
import pandas as pd

from movesense.classifier import BehaviourClassifier, FEATURE_COLUMNS
from movesense.detector import PedestrianDetector
from movesense.features import extract_trajectory_features
from movesense.tracker import SimpleTracker

BEHAVIOUR_COLORS: dict[str, tuple[int, int, int]] = {
    "walking": (0, 220, 120),     # Verde
    "running": (0, 80, 255),      # Laranja/Vermelho
    "loitering": (0, 215, 255),   # Amarelo
    "standing": (255, 200, 0),    # Ciano
}
IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".bmp"}


def _inspect_source(
    input_path: pathlib.Path,
) -> tuple[bool, float, tuple[int, int], list[pathlib.Path]]:
    """Inspect a video file or image-sequence folder and return source metadata."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input source not found: {input_path}")

    if input_path.is_dir():
        image_files = sorted(
            p for p in input_path.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS
        )
        if not image_files:
            raise ValueError(f"No image frames found in directory: {input_path}")

        first_frame = cv2.imread(str(image_files[0]))
        if first_frame is None:
            raise RuntimeError(f"Could not read first image frame: {image_files[0]}")
        height, width = first_frame.shape[:2]
        return True, 25.0, (width, height), image_files

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {input_path}")

    try:
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        if fps <= 0.0 or np.isnan(fps):
            fps = 25.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    finally:
        cap.release()

    return False, fps, (width, height), []


def _iter_source_frames(
    input_path: pathlib.Path,
    is_dir: bool,
    image_files: list[pathlib.Path],
    max_frames: int | None = None,
) -> Iterator[tuple[int, np.ndarray]]:
    """Yield (1-based frame_idx, BGR image) from a video file or image directory."""
    if is_dir:
        for frame_idx, img_path in enumerate(image_files, start=1):
            if max_frames is not None and frame_idx > max_frames:
                break
            frame = cv2.imread(str(img_path))
            if frame is not None:
                yield frame_idx, frame
        return

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {input_path}")

    try:
        frame_idx = 1
        while True:
            if max_frames is not None and frame_idx > max_frames:
                break
            ret, frame = cap.read()
            if not ret:
                break
            yield frame_idx, frame
            frame_idx += 1
    finally:
        cap.release()


def _create_video_writer(
    output_video_path: pathlib.Path,
    fps: float,
    frame_size: tuple[int, int],
) -> cv2.VideoWriter:
    """Create an OpenCV VideoWriter suited to the output file extension."""
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    codec = "mp4v" if output_video_path.suffix.lower() == ".mp4" else "MJPG"
    fourcc = cv2.VideoWriter_fourcc(*codec)
    writer = cv2.VideoWriter(str(output_video_path), fourcc, float(fps), frame_size)
    if not writer.isOpened():
        raise RuntimeError(f"Could not initialize VideoWriter at: {output_video_path}")
    return writer


def _draw_frame_annotations(
    frame: np.ndarray,
    frame_idx: int,
    frame_tracks: pd.DataFrame | None,
    behaviour_map: dict[int, str],
) -> np.ndarray:
    """Draw HUD timestamp, bounding boxes, track IDs, and behaviour labels."""
    annotated = frame.copy()
    cv2.putText(
        annotated,
        f"MoveSense | Frame: {frame_idx:04d}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (240, 240, 240),
        2,
        cv2.LINE_AA,
    )

    if frame_tracks is None or frame_tracks.empty:
        return annotated

    for _, row in frame_tracks.iterrows():
        track_id = int(row["id"])
        x, y, w, h = int(row["x"]), int(row["y"]), int(row["w"]), int(row["h"])
        behaviour = behaviour_map.get(track_id, "unknown")
        color = BEHAVIOUR_COLORS.get(behaviour.lower(), (220, 220, 220))

        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
        label = f"ID {track_id} | {behaviour.upper()}"
        cv2.putText(
            annotated,
            label,
            (x, max(20, y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            color,
            2,
            cv2.LINE_AA,
        )

    return annotated


def run_video_pipeline(
    input_path: pathlib.Path | str,
    output_video_path: pathlib.Path | str,
    output_csv_path: pathlib.Path | str,
    detector: PedestrianDetector | None = None,
    tracker: SimpleTracker | None = None,
    classifier: BehaviourClassifier | None = None,
    fps: float | None = None,
    max_frames: int | None = None,
    smooth_window: int = 1,
    min_track_frames: int = 1,
) -> dict:
    """Run detection, tracking, feature extraction, behaviour classification, and video rendering."""
    src_path = pathlib.Path(input_path)
    out_video = pathlib.Path(output_video_path)
    out_csv = pathlib.Path(output_csv_path)

    is_dir, detected_fps, frame_size, image_files = _inspect_source(src_path)
    effective_fps = float(fps) if fps is not None else detected_fps

    active_detector = detector if detector is not None else PedestrianDetector()
    active_tracker = tracker if tracker is not None else SimpleTracker(iou_threshold=0.3, max_misses=5)

    if classifier is None:
        raise ValueError("A trained BehaviourClassifier must be provided.")

    # Passagem 1: Detecção e Tracking frame a frame
    track_records: list[dict] = []
    frames_processed = 0
    for frame_idx, frame in _iter_source_frames(src_path, is_dir, image_files, max_frames):
        frames_processed += 1
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

    tracks_df = pd.DataFrame(track_records)

    # Extração de features (com suavização/filtro opcionais) e classificação comportamental
    if tracks_df.empty:
        predictions_df = pd.DataFrame(
            columns=["track_id", *FEATURE_COLUMNS, "predicted_behaviour"]
        )
        behaviour_map: dict[int, str] = {}
        tracks_by_frame: dict[int, pd.DataFrame] = {}
    else:
        features_df = extract_trajectory_features(
            tracks_df,
            fps=int(round(effective_fps)),
            smooth_window=smooth_window,
            min_frames=min_track_frames,
        )
        if features_df.empty:
            predictions_df = pd.DataFrame(
                columns=["track_id", *FEATURE_COLUMNS, "predicted_behaviour"]
            )
            behaviour_map = {}
            tracks_by_frame = {}
        else:
            features_df["predicted_behaviour"] = classifier.predict(features_df)
            predictions_df = features_df
            valid_ids = set(predictions_df["track_id"].astype(int))
            tracks_df = tracks_df[tracks_df["id"].isin(valid_ids)].reset_index(drop=True)
            behaviour_map = {
                int(row["track_id"]): str(row["predicted_behaviour"])
                for _, row in predictions_df.iterrows()
            }
            tracks_by_frame = {f: group for f, group in tracks_df.groupby("frame")}

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    predictions_df.to_csv(out_csv, index=False)

    # Passagem 2: Renderização do vídeo anotado
    writer = _create_video_writer(out_video, effective_fps, frame_size)
    try:
        for frame_idx, frame in _iter_source_frames(src_path, is_dir, image_files, max_frames):
            annotated = _draw_frame_annotations(
                frame=frame,
                frame_idx=frame_idx,
                frame_tracks=tracks_by_frame.get(frame_idx),
                behaviour_map=behaviour_map,
            )
            writer.write(annotated)
    finally:
        writer.release()

    return {
        "frames_processed": frames_processed,
        "total_tracks": len(predictions_df),
        "tracks_df": tracks_df,
        "predictions_df": predictions_df,
    }