"""Pedestrian detection module using YOLOv8."""

from dataclasses import dataclass
import numpy as np
from ultralytics import YOLO


@dataclass
class Detection:
    """A single pedestrian detection in a frame.

    Attributes
    ----------
    x : float
        Top-left X coordinate of the bounding box.
    y : float
        Top-left Y coordinate of the bounding box.
    w : float
        Width of the bounding box.
    h : float
        Height of the bounding box.
    conf : float
        Confidence score of the detection (between 0.0 and 1.0).
    """

    x: float
    y: float
    w: float
    h: float
    conf: float


class PedestrianDetector:
    """YOLOv8-based pedestrian detector for single image frames."""

    def __init__(self, model_name: str = "yolov8n.pt", conf_threshold: float = 0.25) -> None:
        """Initialize the pedestrian detector.

        Parameters
        ----------
        model_name : str
            YOLO model weights to load (e.g., 'yolov8n.pt').
        conf_threshold : float
            Minimum confidence threshold to keep a detection.
        """
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        self.person_class_id = 0  # COCO class index for 'person'
        self.model = YOLO(model_name)

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Detect pedestrians in a single video frame.

        Parameters
        ----------
        frame : np.ndarray
            Input image in BGR format (standard OpenCV format).

        Returns
        -------
        list[Detection]
            List of detected pedestrians with bounding box and confidence.
        """
        results = self.model(frame, verbose=False, conf=self.conf_threshold)
        detections: list[Detection] = []

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                cls_id = int(box.cls[0].item())
                # Filtra apenas a classe 0 (pedestres / persons)
                if cls_id != self.person_class_id:
                    continue

                conf = float(box.conf[0].item())
                # Coordenadas em formato xyxy (x1, y1, x2, y2)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                w = x2 - x1
                h = y2 - y1

                detections.append(Detection(x=x1, y=y1, w=w, h=h, conf=conf))

        return detections