"""Empirical benchmark comparing Synchronous vs Asynchronous pipeline FPS (DE-08)."""

from pathlib import Path
import time
import cv2
import pandas as pd

from movesense.async_pipeline import AsyncStreamPipeline
from movesense.detector import PedestrianDetector
from movesense.tracker import SimpleTracker


def main() -> None:
    img_dir = Path("data/MOT17/train/MOT17-09-FRCNN/img1")
    output_csv = Path("results/async_streaming_benchmark.csv")
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    if not img_dir.exists():
        print(f"Error: {img_dir} does not exist.")
        return

    img_files = sorted(img_dir.glob("*.jpg"))[:60]
    frames = [cv2.imread(str(p)) for p in img_files if cv2.imread(str(p)) is not None]
    n_frames = len(frames)

    print("=" * 80)
    print("DE-08: BENCHMARK DE STREAMING (SINCRONO vs ASSINCRONO)")
    print(f"Testando com {n_frames} frames reais de MOT17-09...")
    print("=" * 80)

    # -------------------------------------------------------------
    # 1. Modo Sincrono (Bloqueante)
    # -------------------------------------------------------------
    print("\n[1/2] Executando Pipeline Sincrono tradicional...")
    sync_detector = PedestrianDetector(model_name="yolov8n.pt", conf_threshold=0.50)
    sync_tracker = SimpleTracker(iou_threshold=0.3)

    t0_sync = time.perf_counter()
    for frame in frames:
        detections = sync_detector.detect(frame)
        _ = sync_tracker.update(detections)
    total_time_sync = time.perf_counter() - t0_sync
    fps_sync = n_frames / total_time_sync

    print(f"  -> Tempo total sincrono: {total_time_sync:.2f} s | FPS: {fps_sync:.1f}")

    # -------------------------------------------------------------
    # 2. Modo Assincrono (Desacoplado)
    # -------------------------------------------------------------
    print("\n[2/2] Executando Pipeline Assincrono (DE-08)...")
    async_detector = PedestrianDetector(model_name="yolov8n.pt", conf_threshold=0.50)
    pipeline = AsyncStreamPipeline(detector=async_detector, iou_threshold=0.3)
    pipeline.start()

    t0_async = time.perf_counter()
    for frame in frames:
        _ = pipeline.process_frame(frame)
        # Simula taxa de ingestao da camera/stream (10 ms por frame)
        time.sleep(0.010)

    # Aguarda o worker terminar o ultimo frame
    time.sleep(0.10)
    pipeline.stop()
    total_time_async = time.perf_counter() - t0_async
    fps_async = n_frames / total_time_async

    worker = pipeline.worker
    print(f"  -> Tempo total assincrono: {total_time_async:.2f} s | Ingestao FPS: {fps_async:.1f}")
    print(f"  -> Frames processados pelo YOLO: {worker.processed_count}")
    print(f"  -> Frames descartados (Zero Lag): {worker.dropped_count}")

    # -------------------------------------------------------------
    # Tabela Comparativa de Performance
    # -------------------------------------------------------------
    speedup = fps_async / fps_sync if fps_sync > 0 else 1.0
    summary = [
        {
            "Modo": "Sincrono (Bloqueante)",
            "Frames Totais": n_frames,
            "Tempo Total (s)": round(total_time_sync, 2),
            "Taxa de Stream (FPS)": round(fps_sync, 1),
            "Inferencia Paralela": "Nao (Trava o video)",
            "Atraso (Lag)": "Acumulativo",
        },
        {
            "Modo": "Assincrono (DE-08)",
            "Frames Totais": n_frames,
            "Tempo Total (s)": round(total_time_async, 2),
            "Taxa de Stream (FPS)": round(fps_async, 1),
            "Inferencia Paralela": "Sim (Worker Thread)",
            "Atraso (Lag)": "Zero (Drop on Overrun)",
        },
    ]

    df_summary = pd.DataFrame(summary)
    df_summary.to_csv(output_csv, index=False)

    print("\n" + df_summary.to_string(index=False))
    print(f"\nGanho de Fluidez (Speedup): {speedup:.1f}x mais rapido na exibicao do video!")
    print(f"Resultados salvos em: {output_csv}")


if __name__ == "__main__":
    main()