"""Render synthetic video from MOT ground-truth annotations."""

import pathlib
from collections import defaultdict
import cv2
import numpy as np


def render_synthetic_video(
    gt_path: pathlib.Path,
    output_video_path: pathlib.Path,
    img_w: int = 1920,
    img_h: int = 1080,
    fps: int = 25,
) -> pathlib.Path:
    """Render a synthetic video file (.avi) by drawing bounding boxes from a MOT file.

    Parameters
    ----------
    gt_path : pathlib.Path
        Path to the MOT ground-truth txt file.
    output_video_path : pathlib.Path
        Destination path for the rendered .avi video.
    img_w, img_h : int
        Video resolution (width and height).
    fps : int
        Frames per second for video playback.

    Returns
    -------
    pathlib.Path
        Path to the rendered video file.
    """
    output_video_path.parent.mkdir(parents=True, exist_ok=True)

    # Group detections by frame: {frame_id: [(x, y, w, h, ped_id), ...]}
    frames_data: dict[int, list[tuple[int, int, int, int, int]]] = defaultdict(list)
    max_frame = 0

    lines = gt_path.read_text().strip().splitlines()
    for line in lines:
        if not line:
            continue
        parts = line.split(",")
        frame = int(parts[0])
        ped_id = int(parts[1])
        x, y, w, h = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])

        frames_data[frame].append((x, y, w, h, ped_id))
        if frame > max_frame:
            max_frame = frame

    # Setup OpenCV VideoWriter with standard MJPG codec
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(str(output_video_path), fourcc, float(fps), (img_w, img_h))

    for frame_idx in range(1, max_frame + 1):
        # Background: dark gray canvas (simulating outdoor floor/ground)
        canvas = np.full((img_h, img_w, 3), 40, dtype=np.uint8)

        # Draw frame number timestamp on top-left corner
        cv2.putText(
            canvas,
            f"Frame: {frame_idx:04d}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (200, 200, 200),
            2,
            cv2.LINE_AA,
        )

        # Draw each pedestrian's bounding box and ID label
        for x, y, w, h, ped_id in frames_data.get(frame_idx, []):
            # Draw green bounding box
            cv2.rectangle(canvas, (x, y), (x + w, y + h), (0, 255, 128), 2)

            # Draw pedestrian ID above the box
            label = f"ID: {ped_id}"
            cv2.putText(
                canvas,
                label,
                (x, max(20, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 128),
                2,
                cv2.LINE_AA,
            )

        writer.write(canvas)

    writer.release()
    return output_video_path