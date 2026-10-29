"""Generate synthetic dataset."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from movesense.synthetic import generate_synthetic_dataset

if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent / "data" / "synthetic"
    generate_synthetic_dataset(output_dir)