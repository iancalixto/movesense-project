"""Pedestrian detector using Ultralytics YOLO models."""

from dataclasses import dataclass
import numpy as np
from ultralytics import YOLO


@dataclass(frozen=True)
class Detection:
    """Standardized detection bounding box.

    Attributes
    ----------
    x, y : float
        Top-left coordinates.
    w, h : float
        Width and height of the box.
    conf : float
        Confidence score between 0.0 and 1.0.
    class_id : int
        Class index (0 for person in COCO dataset).
    """

    x: float
    y: float
    w: float
    h: float
    conf: float
    class_id: int = 0


class PedestrianDetector:
    """Wrapper around YOLO for pedestrian detection."""

    def __init__(self, model_name: str = "yolov8n.pt", conf_threshold: float = 0.25) -> None:
        """Initialize the YOLO detector.

        Parameters
        ----------
        model_name : str
            YOLO model weights name or path (default: 'yolov8n.pt').
        conf_threshold : float
            Minimum confidence threshold to keep a detection.
        """
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        self.model = YOLO(model_name)

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Detect pedestrians in a single image/frame.

        Parameters
        ----------
        frame : np.ndarray
            OpenCV image (BGR format).

        Returns
        -------
        list[Detection]
            List of detected pedestrian bounding boxes.
        """
        # Run inference filtering exclusively for class 0 ('person' in COCO)
        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            classes=[0],
            verbose=False,
        )

        detections: list[Detection] = []
        if not results:
            return detections

        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return detections

        # Extract xyxy and confidences
        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        cls_ids = boxes.cls.cpu().numpy().astype(int)

        for i in range(len(xyxy)):
            x1, y1, x2, y2 = xyxy[i]
            w = float(x2 - x1)
            h = float(y2 - y1)
            det = Detection(
                x=float(x1),
                y=float(y1),
                w=w,
                h=h,
                conf=float(confs[i]),
                class_id=int(cls_ids[i]),
            )
            detections.append(det)

        return detections