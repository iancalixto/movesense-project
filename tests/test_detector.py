"""Tests for pedestrian detection module."""

import numpy as np
import pytest

from movesense.detector import PedestrianDetector, Detection


def test_detector_initialization():
    """Verify PedestrianDetector initializes with a lightweight model."""
    detector = PedestrianDetector(model_name="yolov8n.pt", conf_threshold=0.3)
    assert detector.conf_threshold == 0.3
    assert detector.model is not None


def test_detector_predict_on_empty_frame():
    """Verify detector returns an empty list for a blank black canvas."""
    detector = PedestrianDetector(model_name="yolov8n.pt", conf_threshold=0.5)

    # Blank black canvas (no persons)
    blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    detections = detector.detect(blank_frame)

    assert isinstance(detections, list)
    assert len(detections) == 0, "No pedestrians should be detected on a blank black image"


def test_detector_output_structure():
    """Verify Detection dataclass fields match our tracking pipeline contract."""
    det = Detection(x=10.0, y=20.0, w=50.0, h=100.0, conf=0.85, class_id=0)
    assert det.x == 10.0
    assert det.w == 50.0
    assert det.conf == 0.85
    assert det.class_id == 0