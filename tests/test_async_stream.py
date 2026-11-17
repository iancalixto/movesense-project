"""Unit tests for decoupled asynchronous streaming detector and tracker (DE-08)."""

import time
import numpy as np
import pytest

from movesense.async_pipeline import AsyncDetectorWorker, AsyncStreamPipeline
from movesense.detector import Detection


class MockDetector:
    """Mock detector that simulates inference latency without requiring GPU/weights."""

    def __init__(self, latency_s: float = 0.05) -> None:
        self.latency_s = latency_s
        self.call_count = 0

    def detect(self, frame: np.ndarray) -> list[Detection]:
        self.call_count += 1
        time.sleep(self.latency_s)
        # Retorna uma deteccao simulada
        return [Detection(x=100.0, y=100.0, w=50.0, h=120.0, conf=0.9)]


def test_async_worker_lifecycle():
    """Verify that AsyncDetectorWorker starts, processes frames, and stops gracefully."""
    mock = MockDetector(latency_s=0.01)
    worker = AsyncDetectorWorker(detector=mock, max_queue_size=1)
    worker.start()

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Envia frames
    for _ in range(5):
        worker.put_frame(dummy_frame)
        time.sleep(0.015)

    worker.stop()

    assert not worker.is_alive()
    assert worker.processed_count > 0


def test_async_queue_drops_stale_frames_under_load():
    """Verify that worker drops stale frames when camera produces faster than inference."""
    # Detector lento (100 ms de latencia)
    slow_detector = MockDetector(latency_s=0.10)
    worker = AsyncDetectorWorker(detector=slow_detector, max_queue_size=1)
    worker.start()

    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)

    # Ingestao ultrarrapida de 20 frames (simulando stream de alta taxa)
    for _ in range(20):
        worker.put_frame(dummy_frame)
        time.sleep(0.005)

    # Aguarda o worker terminar o frame corrente
    time.sleep(0.15)
    worker.stop()

    # O detector lento deve ter processado bem menos que 20 frames,
    # descartando os intermediarios para evitar atraso (zero lag)
    assert worker.processed_count < 20
    assert worker.dropped_count > 0


def test_async_stream_pipeline_integration():
    """Verify that AsyncStreamPipeline updates tracks with latest detections."""
    mock = MockDetector(latency_s=0.01)
    pipeline = AsyncStreamPipeline(detector=mock, iou_threshold=0.3)
    pipeline.start()

    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Simula stream a 60 FPS (16 ms por frame)
    tracks_seen = []
    for _ in range(10):
        tracks = pipeline.process_frame(dummy_frame)
        tracks_seen.append(tracks)
        time.sleep(0.016)

    pipeline.stop()

    # Como o mock retorna 1 pessoa, o pipeline deve produzir tracks com sucesso
    assert pipeline.capture_frame_count == 10
    assert any(len(t) > 0 for t in tracks_seen)