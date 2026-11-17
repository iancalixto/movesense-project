"""Live visualizer for MoveSense pedestrian tracking and behaviour classification."""

import argparse
from pathlib import Path
import time
import cv2
import numpy as np
import pandas as pd

from movesense.detector import PedestrianDetector
from movesense.rules import RuleEngine
from movesense.tracker import SimpleTracker


def draw_hud(frame: np.ndarray, fps: float, active_tracks: int, total_frames: int) -> None:
    """Draw a semi-transparent HUD bar at the top."""
    h, w, _ = frame.shape
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 45), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    text = f"MoveSense Live | FPS: {fps:.1f} | Pedestres: {active_tracks} | Frame: {total_frames} (Pressione 'q' p/ sair, 'ESPACO' p/ pausar)"
    cv2.putText(frame, text, (15, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (0, 255, 255), 2, cv2.LINE_AA)


def main() -> None:
    parser = argparse.ArgumentParser(description="Visualizador ao vivo MoveSense")
    parser.add_argument(
        "--source",
        type=str,
        default="data/MOT17/train/MOT17-09-FRCNN/img1",
        help="Caminho para pasta de imagens do MOT17, arquivo de video ou '0' para webcam.",
    )
    parser.add_argument("--conf", type=float, default=0.50, help="Limiar de confianca do detector.")
    args = parser.parse_args()

    print("=" * 80)
    print("INICIALIZANDO MOVESENSE VISUALIZER...")
    print("=" * 80)

    detector = PedestrianDetector(model_name="yolov8n.pt", conf_threshold=args.conf)
    tracker = SimpleTracker(iou_threshold=0.3, max_misses=5)
    engine = RuleEngine.from_config("configs/behaviour_rules.json")

    is_webcam = args.source in ("0", "webcam")
    source_path = Path(args.source)

    if is_webcam:
        print("Tentando conectar a Webcam do Mac via AVFoundation...")
        cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
        if not cap.isOpened():
            print("Indice 0 indisponivel. Tentando Indice 1...")
            cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)
        if not cap.isOpened():
            print("Indice 1 indisponivel. Tentando backend padrao...")
            cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("\n[ERRO]: Nao foi possivel acessar a webcam.")
            print("Certifique-se de autorizar a Camera em: Ajustes do Sistema > Privacidade e Seguranca > Camera.")
            return

        img_files = None
        print("WebCam conectada com sucesso!")
    elif source_path.is_dir():
        cap = None
        img_files = sorted(source_path.glob("*.jpg"))
        if not img_files:
            print(f"[ERRO]: Nenhuma imagem .jpg encontrada em {source_path}")
            return
        print(f"Carregando {len(img_files)} frames de {source_path}...")
    else:
        cap = cv2.VideoCapture(str(source_path))
        img_files = None

    track_history = {}
    frame_idx = 0
    paused = False

    t_prev = time.perf_counter()
    fps = 30.0

    window_title = "MoveSense - Live Behaviour Classification"
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)

    print("\nAbrindo janela interativa... Olhe para a janela que vai abrir no seu Mac!")

    while True:
        if not paused:
            if img_files:
                if frame_idx >= len(img_files):
                    frame_idx = 0  # Repete o video em loop
                frame = cv2.imread(str(img_files[frame_idx]))
                frame_idx += 1
            else:
                ret, frame = cap.read()
                if not ret:
                    print("Stream de video finalizado ou sem frames.")
                    break
                frame_idx += 1

            if frame is None:
                continue

            t_now = time.perf_counter()
            dt = t_now - t_prev
            t_prev = t_now
            fps = 1.0 / dt if dt > 0 else 30.0

            # 1. Deteccao + Rastreamento
            detections = detector.detect(frame)
            active_tracks = tracker.update(detections)

            # 2. Avaliacao Comportamental
            for t in active_tracks:
                tid = t.track_id
                if tid not in track_history:
                    track_history[tid] = []
                track_history[tid].append({
                    "frame": frame_idx,
                    "track_id": tid,
                    "x": float(t.x),
                    "y": float(t.y),
                    "w": float(t.w),
                    "h": float(t.h),
                })
                if len(track_history[tid]) > 60:
                    track_history[tid].pop(0)

                df_track = pd.DataFrame(track_history[tid])
                eval_res = engine.evaluate_track(df_track, fps=30.0)
                behaviour = eval_res["primary_behaviour"]
                anomalies = eval_res["anomalies"]
                speed_bl = eval_res["mean_speed_bl_s"]

                # Cores por comportamento
                if anomalies or eval_res["is_laydown"]:
                    box_color = (0, 0, 255)      # Vermelho (anomalia ou queda)
                elif behaviour == "walking":
                    box_color = (0, 255, 0)      # Verde (caminhando)
                elif behaviour == "running":
                    box_color = (0, 255, 255)    # Amarelo (correndo)
                elif behaviour == "loitering":
                    box_color = (255, 165, 0)    # Laranja (perambulando)
                else:
                    box_color = (255, 255, 0)    # Ciano (parado / standing)

                x, y, w_box, h_box = int(t.x), int(t.y), int(t.w), int(t.h)
                cv2.rectangle(frame, (x, y), (x + w_box, y + h_box), box_color, 2)

                label = f"ID:{tid} {behaviour.upper()} ({speed_bl:.2f} bl/s)"
                if anomalies:
                    label += f" | {anomalies[0]}"

                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                cv2.rectangle(frame, (x, max(0, y - 20)), (x + tw + 6, max(20, y)), box_color, -1)
                cv2.putText(frame, label, (x + 3, max(15, y - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

            draw_hud(frame, fps, len(active_tracks), frame_idx)

        cv2.imshow(window_title, frame)

        key = cv2.waitKey(20) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused

    if cap:
        cap.release()
    cv2.destroyAllWindows()
    print("Visualizacao encerrada com sucesso.")


if __name__ == "__main__":
    main()