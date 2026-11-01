"""Inspect a MOT dataset and display key summary statistics.

Run:
    python scripts/inspect_dataset.py
"""

import pathlib
from movesense.loader import load_mot_file


def main() -> None:
    gt_file = pathlib.Path("data/synthetic/gt.txt")
    if not gt_file.exists():
        raise FileNotFoundError(
            f"Ground-truth file not found at {gt_file}. Run 'make step-02' first to generate it!"
        )

    df = load_mot_file(gt_file)

    print("=" * 60)
    print(" MoveSense · MOT Dataset Summary")
    print("=" * 60)
    print(f"Total detections  : {len(df)}")
    print(f"Total frames      : {df['frame'].nunique()} (from {df['frame'].min()} to {df['frame'].max()})")
    print(f"Unique pedestrians: {df['id'].nunique()} (IDs: {sorted(df['id'].unique().tolist())})")
    print("\nPreview of first 5 rows:")
    print("-" * 60)
    print(df.head(5).to_string(index=False))
    print("=" * 60)


if __name__ == "__main__":
    main()