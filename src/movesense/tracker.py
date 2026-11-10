"""Pedestrian tracking module using IoU association across consecutive frames."""

from dataclasses import dataclass
from movesense.detector import Detection


@dataclass
class Track:
    """An active pedestrian track.

    Attributes
    ----------
    track_id : int
        Unique identity persistent across frames.
    x, y : float
        Current top-left bounding box coordinates.
    w, h : float
        Current width and height of the bounding box.
    conf : float
        Confidence of the latest matched detection.
    age : int
        Number of frames this track has been alive.
    misses : int
        Number of consecutive frames without a detection match.
    """

    track_id: int
    x: float
    y: float
    w: float
    h: float
    conf: float
    age: int = 1
    misses: int = 0


def calculate_iou(
    box_a: tuple[float, float, float, float],
    box_b: tuple[float, float, float, float],
) -> float:
    """Calculate Intersection over Union (IoU) between two bounding boxes.

    Each box is in (x, y, w, h) format.
    """
    xa, ya, wa, ha = box_a
    xb, yb, wb, hb = box_b

    # Converte para cantos (x1, y1, x2, y2)
    x1_a, y1_a, x2_a, y2_a = xa, ya, xa + wa, ya + ha
    x1_b, y1_b, x2_b, y2_b = xb, yb, xb + wb, yb + hb

    # Retângulo de intersecção
    inter_x1 = max(x1_a, x1_b)
    inter_y1 = max(y1_a, y1_b)
    inter_x2 = min(x2_a, x2_b)
    inter_y2 = min(y2_a, y2_b)

    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    intersection = inter_w * inter_h

    # Área de união
    area_a = wa * ha
    area_b = wb * hb
    union = area_a + area_b - intersection

    if union <= 0.0:
        return 0.0
    return intersection / union


class SimpleTracker:
    """Multi-object tracker associating detections across frames using IoU."""

    def __init__(self, iou_threshold: float = 0.3, max_misses: int = 3) -> None:
        """Initialize the tracker.

        Parameters
        ----------
        iou_threshold : float
            Minimum IoU to consider a detection belonging to an existing track.
        max_misses : int
            Number of consecutive missed frames before discarding a lost track.
        """
        self.iou_threshold = iou_threshold
        self.max_misses = max_misses
        self.next_id = 1
        self.tracks: list[Track] = []

    def update(self, detections: list[Detection]) -> list[Track]:
        """Update active tracks with new detections from the current frame.

        Parameters
        ----------
        detections : list[Detection]
            Detections observed in the current frame.

        Returns
        -------
        list[Track]
            Currently active tracks with updated coordinates and persistent IDs.
        """
        updated_tracks: list[Track] = []
        unmatched_detections = list(detections)

        # 1. Tenta associar os tracks existentes às novas detecções com maior IoU
        for track in self.tracks:
            best_iou = 0.0
            best_det_idx = -1

            track_box = (track.x, track.y, track.w, track.h)
            for idx, det in enumerate(unmatched_detections):
                det_box = (det.x, det.y, det.w, det.h)
                iou = calculate_iou(track_box, det_box)
                if iou > best_iou:
                    best_iou = iou
                    best_det_idx = idx

            if best_iou >= self.iou_threshold and best_det_idx >= 0:
                # Match encontrado: atualiza a posição e reseta as perdas (misses)
                matched_det = unmatched_detections.pop(best_det_idx)
                track.x = matched_det.x
                track.y = matched_det.y
                track.w = matched_det.w
                track.h = matched_det.h
                track.conf = matched_det.conf
                track.age += 1
                track.misses = 0
                updated_tracks.append(track)
            else:
                # Nenhum pedestre detectado neste frame próximo da posição anterior
                track.misses += 1
                if track.misses <= self.max_misses:
                    updated_tracks.append(track)

        # 2. As detecções que sobraram sem correspondência viram novos tracks (novos IDs)
        for new_det in unmatched_detections:
            new_track = Track(
                track_id=self.next_id,
                x=new_det.x,
                y=new_det.y,
                w=new_det.w,
                h=new_det.h,
                conf=new_det.conf,
            )
            self.next_id += 1
            updated_tracks.append(new_track)

        self.tracks = updated_tracks
        # Retorna apenas os tracks visíveis no frame atual
        return [t for t in self.tracks if t.misses == 0]