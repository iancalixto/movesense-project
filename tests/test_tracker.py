"""Tests for pedestrian multi-object tracking module."""

import pytest
from movesense.detector import Detection
from movesense.tracker import SimpleTracker, Track


def test_tracker_assigns_new_id():
    """Verify tracker assigns a new ID to the first detection."""
    tracker = SimpleTracker(iou_threshold=0.3)
    detections_frame1 = [Detection(x=100.0, y=100.0, w=50.0, h=100.0, conf=0.9)]

    tracks = tracker.update(detections_frame1)

    assert len(tracks) == 1
    assert tracks[0].track_id == 1
    assert tracks[0].x == 100.0


def test_tracker_maintains_consistent_id_across_frames():
    """Verify tracker preserves track_id for moving pedestrian with overlapping box."""
    tracker = SimpleTracker(iou_threshold=0.3)

    # Frame 1: Pessoa em (100, 100) -> ganha ID 1
    tracks_f1 = tracker.update([Detection(x=100.0, y=100.0, w=50.0, h=100.0, conf=0.9)])
    assert tracks_f1[0].track_id == 1

    # Frame 2: Pessoa deu um passo para (105, 102) -> IoU alto, deve manter ID 1!
    tracks_f2 = tracker.update([Detection(x=105.0, y=102.0, w=50.0, h=100.0, conf=0.88)])
    assert len(tracks_f2) == 1
    assert tracks_f2[0].track_id == 1, "O ID deve continuar sendo 1 entre frames contínuos!"


def test_tracker_assigns_distinct_ids_for_separated_detections():
    """Verify two distinct persons get distinct IDs (ID 1 and ID 2)."""
    tracker = SimpleTracker(iou_threshold=0.3)

    # Duas pessoas no mesmo frame, bem separadas
    detections = [
        Detection(x=50.0, y=50.0, w=50.0, h=100.0, conf=0.9),
        Detection(x=500.0, y=500.0, w=50.0, h=100.0, conf=0.92),
    ]
    tracks = tracker.update(detections)

    assert len(tracks) == 2
    ids = {t.track_id for t in tracks}
    assert ids == {1, 2}, f"Esperava IDs {{1, 2}}, obteve {ids}"