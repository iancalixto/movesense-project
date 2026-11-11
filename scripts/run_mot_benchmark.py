"""Run unified MOT17 (baseline) + MOT20 (crowding stress test) tracking benchmark.

Automatically validates split leakage from configs/splits/mot_sequences.json,
evaluates all available local sequences, and reports MOT17 and MOT20 separately.

Examples:
    python scripts/run_mot_benchmark.py
    python scripts/run_mot_benchmark.py --max-frames 100 --conf 0.50
"""

import argparse
import json
import pathlib
import pandas as pd

from movesense.benchmark import (
    discover_mot_sequences,
    evaluate_mot_sequence,
    summarize_by_dataset,
    validate_no_sequence_leakage,
)
from movesense.detector import PedestrianDetector
from movesense.tracker import SimpleTracker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate MoveSense across MOT17 and MOT20 benchmarks without regime mixing."
    )
    parser.add_argument(
        "--splits-config",
        type=pathlib.Path,
        default=pathlib.Path("configs/splits/mot_sequences.json"),
        help="Path to frozen sequence splits JSON.",
    )
    parser.add_argument(
        "--mot17-dir",
        type=pathlib.Path,
        default=pathlib.Path("data/MOT17/train"),
        help="Root directory of MOT17 training sequences.",
    )
    parser.add_argument(
        "--mot20-dir",
        type=pathlib.Path,
        default=pathlib.Path("data/MOT20/train"),
        help="Root directory of MOT20 training sequences.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=60,
        help="Max initial frames per sequence (default: 60 for fast multi-sequence CPU benchmark).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="YOLO model weights (default: yolov8n.pt).",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.50,
        help="Detector confidence threshold (default: 0.50).",
    )
    parser.add_argument(
        "--iou-thresh",
        type=float,
        default=0.50,
        help="IoU threshold for matching predictions to GT (default: 0.50).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # 1. Valida governança de splits (impede leakage entre variantes DPM/FRCNN/SDP)
    splits = json.loads(args.splits_config.read_text())
    mot17_cfg = splits["mot17_baseline"]
    validate_no_sequence_leakage(mot17_cfg["dev"], mot17_cfg["eval"])
    print("✅ Split governance check passed (0 sequence leakage).")

    split_lookup = {s: "dev" for s in mot17_cfg["dev"]}
    split_lookup.update({s: "eval" for s in mot17_cfg["eval"]})
    camera_lookup = mot17_cfg.get("camera_metadata", {})

    # 2. Descobre sequências disponíveis localmente em MOT17 e MOT20
    sequences: list[dict] = []
    for ds_name, root in [("MOT17", args.mot17_dir), ("MOT20", args.mot20_dir)]:
        found = discover_mot_sequences(root, dataset_name=ds_name, preferred_variant="FRCNN")
        if not found:
            print(f"⚠️  {ds_name} não encontrado em {root} (pulando por enquanto).")
        else:
            print(f"📂 {ds_name}: {len(found)} sequência(s) única(s) encontrada(s).")
            sequences.extend(found)

    if not sequences:
        raise FileNotFoundError("Nenhuma sequência MOT17 ou MOT20 encontrada para avaliar.")

    print(f"\n🚀 Carregando {args.model} (conf={args.conf})...")
    detector = PedestrianDetector(model_name=args.model, conf_threshold=args.conf)

    # 3. Avalia cada sequência com um tracker novo e isolado
    rows: list[dict] = []
    for item in sequences:
        seq_name = item["sequence"]
        print(f"   → Avaliando [{item['dataset']}] {seq_name} ({args.max_frames} frames)...")
        fresh_tracker = SimpleTracker(iou_threshold=0.3, max_misses=5)
        result = evaluate_mot_sequence(
            seq_dir=item["path"],
            dataset_name=item["dataset"],
            detector=detector,
            tracker=fresh_tracker,
            max_frames=args.max_frames,
            iou_threshold=args.iou_thresh,
        )
        result["split"] = split_lookup.get(seq_name, "eval")
        result["camera"] = camera_lookup.get(seq_name, "stationary")
        rows.append(result)

    per_seq_df = pd.DataFrame(rows)
    summary_df = summarize_by_dataset(per_seq_df)

    # 4. Exibe tabelas separadas por sequência e por regime (MOT17 vs MOT20)
    print("\n" + "=" * 96)
    print("📊 RESULTADOS POR SEQUÊNCIA")
    print("=" * 96)
    print(f"{'Dataset':<7} | {'Sequência':<16} | {'Split':<5} | {'Câmera':<10} | {'MOTA':>7} | {'Prec':>7} | {'Rec':>7} | {'IDSW':>5}")
    print("-" * 96)
    for _, r in per_seq_df.iterrows():
        print(
            f"{r['dataset']:<7} | {r['sequence']:<16} | {r['split']:<5} | {r['camera']:<10} | "
            f"{r['mota']*100:>6.1f}% | {r['precision']*100:>6.1f}% | {r['recall']*100:>6.1f}% | {int(r['id_switches']):>5d}"
        )

    print("\n" + "=" * 96)
    print("🏛️  RESUMO POR REGIME (MOT17 Baseline vs. MOT20 Crowding Stress Test)")
    print("=" * 96)
    print(f"{'Dataset':<8} | {'Seqs':>4} | {'Frames':>6} | {'GT Boxes':>8} | {'MOTA':>7} | {'Prec':>7} | {'Rec':>7} | {'IDSW':>5}")
    print("-" * 96)
    for _, r in summary_df.iterrows():
        print(
            f"{r['dataset']:<8} | {int(r['sequences']):>4d} | {int(r['frames_evaluated']):>6d} | "
            f"{int(r['total_gt']):>8d} | {r['mota']*100:>6.1f}% | {r['precision']*100:>6.1f}% | "
            f"{r['recall']*100:>6.1f}% | {int(r['id_switches']):>5d}"
        )
    print("=" * 96)

    per_seq_out = pathlib.Path("results/mot_benchmark_per_sequence.csv")
    summary_out = pathlib.Path("results/mot_benchmark_summary.csv")
    per_seq_out.parent.mkdir(parents=True, exist_ok=True)
    per_seq_df.to_csv(per_seq_out, index=False)
    summary_df.to_csv(summary_out, index=False)
    print(f"✅ Salvo por sequência: {per_seq_out}")
    print(f"✅ Salvo por regime   : {summary_out}\n")


if __name__ == "__main__":
    main()