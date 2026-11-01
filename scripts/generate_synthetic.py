"""Generate synthetic pedestrian tracking dataset.

Run:
    python scripts/generate_synthetic.py
"""

import pathlib
from movesense.synthetic import generate_synthetic_mot


def main() -> None:
    output_dir = pathlib.Path("data/synthetic")
    output_path = output_dir / "gt.txt"

    print("Generating synthetic MOT ground-truth dataset...")
    generate_synthetic_mot(
        output_path=output_path,
        n_pedestrians=5,
        n_frames=100,
        seed=2026,
    )
    print(f"Dataset successfully created at: {output_path}")


if __name__ == "__main__":
    main()