"""Extract trajectory kinematic features from tracked pedestrians.

Run:
    python scripts/extract_features.py
"""

import pathlib
import pandas as pd
from movesense.features import extract_trajectory_features
from movesense.loader import load_mot_file


def classify_preliminary_behaviour(row: pd.Series) -> str:
    """Classify physical behaviour based on kinematic rules."""
    if row["mean_speed"] < 15.0:
        return "standing"
    if row["confinement_radius"] < 50.0:
        return "loitering"
    if row["mean_speed"] > 250.0:
        return "running"
    return "walking"


def main() -> None:
    tracks_path = pathlib.Path("data/synthetic/tracks.txt")
    output_features_path = pathlib.Path("data/synthetic/trajectory_features.csv")

    if not tracks_path.exists():
        raise FileNotFoundError(
            f"Tracks not found at {tracks_path}. Run 'make step-07' first!"
        )

    print("Loading tracked trajectories from:", tracks_path)
    tracks_df = load_mot_file(tracks_path)

    print("Extracting kinematic physical features (speed, accel, confinement)...")
    features_df = extract_trajectory_features(tracks_df, fps=25)

    # Adiciona a interpretação preliminar de comportamento
    features_df["heuristic_label"] = features_df.apply(classify_preliminary_behaviour, axis=1)

    output_features_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(output_features_path, index=False)

    print("\n" + "=" * 75)
    print("📊 TABELA DE FEATURES CINEMÁTICAS POR PEDESTRE (MoveSense):")
    print("=" * 75)
    for _, r in features_df.iterrows():
        print(
            f"Pedestre #{int(r['track_id']):<2} | "
            f"Duração: {int(r['duration_frames']):<3} frames | "
            f"Vel. Média: {r['mean_speed']:>6.1f} px/s | "
            f"Raio Conf.: {r['confinement_radius']:>6.1f} px | "
            f"Comportamento: [{r['heuristic_label'].upper()}]"
        )
    print("=" * 75)
    print(f"\nTabela de features para ML salva com sucesso em: {output_features_path}")


if __name__ == "__main__":
    main()