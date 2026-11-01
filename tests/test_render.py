"""Tests for synthetic video rendering module."""

import pathlib
import tempfile
import cv2

from movesense.synthetic import generate_synthetic_mot
from movesense.render import render_synthetic_video


def test_render_creates_video_file():
    """Verify that render_synthetic_video produces a valid readable video."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = pathlib.Path(tmp_dir)
        gt_file = tmp_path / "gt.txt"
        video_file = tmp_path / "synthetic.avi"

        # Generate a small ground-truth sample (2 pedestrians, 5 frames)
        generate_synthetic_mot(gt_file, n_pedestrians=2, n_frames=5, seed=2026, img_w=640, img_h=480)

        # Render video
        render_synthetic_video(gt_path=gt_file, output_video_path=video_file, img_w=640, img_h=480, fps=10)

        # Assert file was created and is non-empty
        assert video_file.exists(), "Video file was not created"
        assert video_file.stat().st_size > 0, "Video file is empty (0 bytes)"

        # Assert OpenCV can open and read frames from the video
        cap = cv2.VideoCapture(str(video_file))
        assert cap.isOpened(), "OpenCV cannot open the rendered video"
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        assert frame_count == 5, f"Expected 5 frames, got {frame_count}"