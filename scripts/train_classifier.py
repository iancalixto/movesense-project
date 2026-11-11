"""Train behaviour classifier and predict behaviours on tracked trajectories.

Run:
    python scripts/train_classifier.py
"""

import pathlib
import numpy as np
import pandas as pd

from movesense.classifier import BehaviourClassifier


def build_labeled_training_corpus(seed: int = 2026) -> pd.DataFrame:
    """Create a realistic balanced training corpus across 4 behaviour classes."""
    rng = np.random.default_rng(seed)
    rows = []

    for i in range(15):  # Standing
        rows.append({
            "duration_frames": int(rng.integers(30, 100)),
            "mean_speed": float(rng.uniform(0.0, 8.0)),
            "max_speed": float(rng.uniform(0.0, 15.0)),
            "std_speed": float(rng.uniform(0.0, 3.0)),
            "mean_acceleration": float(rng.uniform(-2.0, 2.0)),
            "confinement_radius": float(rng.uniform(0.0, 10.0)),
            "label": "standing",
        })

    for i in range(15):  # Loitering
        rows.append({
            "duration_frames": int(rng.integers(50, 100)),
            "mean_speed": float(rng.uniform(15.0, 45.0)),
            "max_speed": float(rng.uniform(25.0, 70.0)),
            "std_speed": float(rng.uniform(5.0, 15.0)),
            "mean_acceleration": float(rng.uniform(-5.0, 5.0)),
            "confinement_radius": float(rng.uniform(12.0, 48.0)),
            "label": "loitering",
        })

    for i in range(15):  # Walking
        rows.append({
            "duration_frames": int(rng.integers(40, 100)),
            "mean_speed": float(rng.uniform(55.0, 180.0)),
            "max_speed": float(rng.uniform(90.0, 240.0)),
            "std_speed": float(rng.uniform(8.0, 30.0)),
            "mean_acceleration": float(rng.uniform(-10.0, 10.0)),
            "confinement_radius": float(rng.uniform(80.0, 450.0)),
            "label": "walking",
        })

    for i in range(15):  # Running
        rows.append({
            "duration_frames": int(rng.integers(20, 80)),
            "mean_speed": float(rng.uniform(260.0, 750.0)),
            "max_speed": float(rng.uniform(350.0, 950.0)),
            "std_speed": float(rng.uniform(25.0, 90.0)),
            "mean_acceleration": float(rng.uniform(-20.0, 40.0)),
            "confinement_radius": float(rng.uniform(250.0, 900.0)),
            "label": "running",
        })

    return pd.DataFrame(rows)


def main() -> None:
    features_path = pathlib.Path("data/synthetic/trajectory_features.csv")
    output_preds_path = pathlib.Path("data/synthetic/behaviour_predictions.csv")

    if not features_path.exists():
        raise FileNotFoundError(
            f"Features file not found at {features_path}. Run 'make step-08' first!"
        )

    print("1. Training Random Forest BehaviourClassifier (60 labeled samples)...")
    train_df = build_labeled_training_corpus(seed=2026)
    clf = BehaviourClassifier(n_estimators=50, random_state=42)
    metrics = clf.train(train_df, target_col="label", test_size=0.25)

    print("\n" + "=" * 65)
    print("📈 AVALIAÇÃO DO MODELO NO CONJUNTO DE TESTE (Test Split 25%):")
    print("=" * 65)
    print(f"Acurácia Global : {metrics['accuracy']*100:.1f}%")
    print(f"Macro F1-Score  : {metrics['macro_f1']*100:.1f}%")
    print("\nClassification Report:")
    print(metrics["classification_report"])

    print("=" * 65)
    print("🔮 PREVISÃO NOS PEDESTRES RASTREADOS DO VÍDEO SINTÉTICO:")
    print("=" * 65)
    video_features = pd.read_csv(features_path)
    video_features["predicted_behaviour"] = clf.predict(video_features)

    for _, row in video_features.iterrows():
        print(
            f"Pedestre #{int(row['track_id']):<2} | "
            f"Duração: {int(row['duration_frames']):<3} frames | "
            f"Vel. Média: {row['mean_speed']:>5.1f} px/s | "
            f"Raio Conf.: {row['confinement_radius']:>5.1f} px | "
            f"Previsto (ML): [{row['predicted_behaviour'].upper()}]"
        )

    video_features.to_csv(output_preds_path, index=False)
    print("=" * 65)
    print(f"\nPrevisões finais salvas em: {output_preds_path}")


if __name__ == "__main__":
    main()