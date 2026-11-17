"""Evaluate MoveSense behaviour classification against JackRabbot (JRDB-Act) benchmark (DS-10)."""

from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report

from movesense.jrdb_loader import JRDBLoader
from movesense.rules import RuleEngine


def main() -> None:
    # Aceita tanto data/sample_jrdb.json quanto data/sample_jrdb/stanford_campus_sample.json
    candidates = [
        Path("data/sample_jrdb.json"),
        Path("data/sample_jrdb/stanford_campus_sample.json"),
    ]
    sample_file = next((p for p in candidates if p.exists()), None)

    output_csv = Path("results/jrdb_action_benchmark.csv")
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    if not sample_file:
        print("Erro: Arquivo data/sample_jrdb.json nao encontrado.")
        return

    print("=" * 80)
    print("DS-10: BENCHMARK DE ACOES - STANFORD JACKRABBOT DATASET (JRDB-Act)")
    print(f"Carregando sequencia: {sample_file} via JRDBLoader...")
    print("=" * 80)

    # 1. Carrega ground-truth do JackRabbot com o adaptador oficial
    loader = JRDBLoader(mapping_config_path="configs/jrdb_action_mapping.json")
    df_labels = loader.load_labels(sample_file)

    # 2. Avalia cada pedestre com o RuleEngine
    engine = RuleEngine.from_config("configs/behaviour_rules.json")

    results = []
    y_true = []
    y_pred = []

    for tid, group in df_labels.groupby("track_id"):
        gt_action = group["action"].iloc[0]
        eval_res = engine.evaluate_track(group, fps=30.0)
        pred_action = eval_res["primary_behaviour"]

        y_true.append(gt_action)
        y_pred.append(pred_action)

        results.append({
            "Track ID": tid,
            "Frames": len(group),
            "Velocidade (corpos/s)": eval_res["mean_speed_bl_s"],
            "Aspect Ratio": eval_res["median_aspect_ratio"],
            "Acao Real (JRDB-Act)": gt_action,
            "Predicao MoveSense": pred_action,
            "Status": "CORRETO" if gt_action == pred_action else "DIVERGENTE",
        })

    df_results = pd.DataFrame(results)
    df_results.to_csv(output_csv, index=False)

    print("\n" + df_results.to_string(index=False))

    # 3. Metricas Globais
    acc = accuracy_score(y_true, y_pred)
    print(f"\nAcuracia Global no JRDB-Act: {acc * 100:.1f}%\n")
    print("Relatorio Cientifico de Classificacao:")
    print(classification_report(y_true, y_pred, zero_division=0))

    print(f"\nResultados salvos com sucesso em: {output_csv}")


if __name__ == "__main__":
    main()