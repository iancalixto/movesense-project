"""Asynchronous and decoupled streaming pipeline for MoveSense.

Decouples high-frequency frame ingestion from deep-learning inference using
a producer-consumer threading model and zero-lag drop-on-overrun queues.
"""

from queue import Empty, Full, Queue
import threading
from typing import Any, List, Optional
import numpy as np


class AsyncDetectorWorker:
    """Background worker thread running object detection without blocking stream ingestion."""

    def __init__(self, detector: Any, max_queue_size: int = 1) -> None:
        """Initialize the async detector worker.

        Parameters
        ----------
        detector : Any
            Detector instance implementing a `.detect(frame)` method.
        max_queue_size : int, default 1
            Maximum frame queue size. Keeping it at 1 drops stale frames to enforce zero lag.
        """
        self.detector = detector
        self.queue: Queue[np.ndarray] = Queue(maxsize=max_queue_size)
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

        self._lock = threading.Lock()
        self.latest_detections: List[Any] = []
        self.processed_count: int = 0
        self.dropped_count: int = 0

    def start(self) -> None:
        """Start the background detector worker thread."""
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Gracefully stop the background worker thread."""
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def is_alive(self) -> bool:
        """Check if worker thread is running."""
        return self.thread is not None and self.thread.is_alive()

    def put_frame(self, frame: np.ndarray) -> None:
        """Enqueue a new frame for inference, dropping stale frames if queue is full."""
        try:
            self.queue.put_nowait(frame)
        except Full:
            # Zero-Lag policy: drop stale frame and insert newest
            try:
                self.queue.get_nowait()
                self.dropped_count += 1
            except Empty:
                pass
            try:
                self.queue.put_nowait(frame)
            except Full:
                pass

    def get_latest_detections(self) -> List[Any]:
        """Fetch the most recent detection results thread-safely."""
        with self._lock:
            return list(self.latest_detections)

    def _run(self) -> None:
        """Worker thread loop consuming frames and executing detection."""
        while not self.stop_event.is_set():
            try:
                frame = self.queue.get(timeout=0.05)
            except Empty:
                continue

            try:
                detections = self.detector.detect(frame)
                with self._lock:
                    self.latest_detections = detections
                    self.processed_count += 1
            except Exception as e:
                print(f"[AsyncDetectorWorker Error]: {e}")
            finally:
                self.queue.task_done()


class AsyncStreamPipeline:
    """Real-time streaming pipeline combining high-rate tracking with async detection."""

    def __init__(
        self,
        detector: Any,
        tracker: Any,
        max_queue_size: int = 1,
    ) -> None:
        """Initialize the pipeline."""
        self.worker = AsyncDetectorWorker(detector=detector, max_queue_size=max_queue_size)
        self.tracker = tracker
        self.capture_frame_count: int = 0

    def start(self) -> None:
        """Start the pipeline background services."""
        self.worker.start()

    def stop(self) -> None:
        """Stop background services."""
        self.worker.stop()

    def process_frame(self, frame: np.ndarray) -> List[Any]:
        """Ingest a video frame, update tracks, and schedule async inference.

        Parameters
        ----------
        frame : np.ndarray
            Current video frame in BGR format.

        Returns
        -------
        List[Any]
            Active tracks in the current frame.
        """
        self.capture_frame_count += 1

        # Enqueue frame for non-blocking background inference
        self.worker.put_frame(frame)

        # Update tracker with latest available detections
        latest_detections = self.worker.get_latest_detections()
        active_tracks = self.tracker.update(latest_detections)

        return active_tracks