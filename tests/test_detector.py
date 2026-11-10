"""Tests for the pedestrian detector module using YOLOv8."""

import numpy as np
import pytest
from movesense.detector import Detection, PedestrianDetector


def test_detection_dataclass():
    """Verify that the Detection dataclass stores bounding box coordinates and confidence."""
    det = Detection(x=100.0, y=150.0, w=50.0, h=120.0, conf=0.85)

    assert det.x == 100.0
    assert det.y == 150.0
    assert det.w == 50.0
    assert det.h == 120.0
    assert det.conf == 0.85


def test_detector_initialization():
    """Verify that PedestrianDetector initializes with model name and confidence threshold."""
    detector = PedestrianDetector(model_name="yolov8n.pt", conf_threshold=0.3)

    assert detector.model_name == "yolov8n.pt"
    assert detector.conf_threshold == 0.3
    assert detector.person_class_id == 0


def test_detector_inference_on_dummy_frame():
    """Verify that calling detect() on an image frame returns a list of Detections."""
    detector = PedestrianDetector(model_name="yolov8n.pt", conf_threshold=0.25)

    # Cria uma imagem de teste (480x640 com 3 canais de cor)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    detections = detector.detect(dummy_frame)

    # Em uma imagem preta não há pedestres, deve retornar uma lista vazia válida
    assert isinstance(detections, list)
    assert len(detections) == 0          