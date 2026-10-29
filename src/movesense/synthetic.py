"""Synthetic dataset generation for MoveSense.

This module generates synthetic MOT17-format datasets with known pedestrian
trajectories and behaviors for testing and development.

**Why synthetic data?**
- Real datasets (MOT17, JRDB) are limited in size and diversity
- Synthetic data lets us control ground truth: exact trajectories, labels, behaviors
- We generate SYN-01 to SYN-12 with varying scenarios:
  - SYN-01–04: Urban crowded scenes (dense pedestrian traffic)
  - SYN-05–08: Sparse outdoor (park, street, open space)
  - SYN-09–12: Mixed scenarios (entrances, corridors, transitions)

**Output format: MOT17**
- video: data/synthetic/SYN-NN.avi (30 fps, 1920×1080)
- labels: data/synthetic/SYN-NN/gt/gt.txt (MOT format: <frame>, <id>, <x>, <y>, <w>, <h>, <conf>, <class>, <vis>)
"""

from pathlib import Path
from typing import Optional


def generate_synthetic_dataset(output_dir: Optional[Path] = None) -> None:
    """Generate synthetic MOT17-format datasets (SYN-01 to SYN-12).
    
    Args:
        output_dir: Path to data/synthetic. If None, uses data/synthetic/ relative to project root.
    
    **Implementation plan (stub for now):**
    1. For each dataset SYN-01 to SYN-12:
       - Generate random pedestrian trajectories (linear, circular, crossing)
       - Render synthetic video (1920×1080, 30 fps, 300 frames)
       - Write MOT17 ground truth labels (gt.txt)
    2. Store in data/synthetic/SYN-NN/ with structure:
       - SYN-NN/SYN-NN.avi (video)
       - SYN-NN/gt/gt.txt (labels)
    
    **Seed: 2026 (for reproducibility)**
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent / "data" / "synthetic"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"TODO: Implement synthetic dataset generation in {output_dir}")
    print("Datasets to generate: SYN-01 to SYN-12")
    print("  - Each: 1920×1080, 30 fps, 300 frames")
    print("  - MOT17 format (gt.txt)")
    print("  - Seed: 2026")