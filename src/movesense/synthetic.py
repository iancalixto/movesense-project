"""Synthetic MOT ground-truth generator.

Generates reproducible pedestrian trajectories in standard MOT format:
    frame, id, x, y, w, h, conf, class, visibility
"""

import pathlib
import numpy as np


def generate_synthetic_mot(
    output_path: pathlib.Path,
    n_pedestrians: int = 5,
    n_frames: int = 100,
    seed: int = 2026,
    img_w: int = 1920,
    img_h: int = 1080,
) -> pathlib.Path:
    """Generate a synthetic MOT ground-truth file.

    Parameters
    ----------
    output_path : pathlib.Path
        Target path for the generated gt.txt file.
    n_pedestrians : int
        Number of simulated pedestrians.
    n_frames : int
        Total frames of simulation.
    seed : int
        Random seed for reproducibility.
    img_w : int
        Width of the simulated camera frame.
    img_h : int
        Height of the simulated camera frame.

    Returns
    -------
    pathlib.Path
        The path to the generated file.
    """
    rng = np.random.default_rng(seed)

    # Standard pedestrian bounding-box size (width x height)
    bbox_w, bbox_h = 64, 128

    lines: list[str] = []

    for ped_id in range(1, n_pedestrians + 1):
        # Initial starting coordinates
        x = float(rng.integers(0, img_w - bbox_w))
        y = float(rng.integers(0, img_h - bbox_h))

        # Velocity vectors (pixels per frame)
        vx = float(rng.uniform(-3.0, 3.0))
        vy = float(rng.uniform(-2.0, 2.0))

        for frame in range(1, n_frames + 1):
            # Update position with small random walk noise
            x = np.clip(x + vx + rng.normal(0, 1.0), 0, img_w - bbox_w)
            y = np.clip(y + vy + rng.normal(0, 1.0), 0, img_h - bbox_h)

            # Standard 9-column MOT format
            line = f"{frame},{ped_id},{int(x)},{int(y)},{bbox_w},{bbox_h},1,1,1.0"
            lines.append(line)

    # Sort primarily by frame, secondarily by pedestrian id
    lines.sort(key=lambda item: (int(item.split(",")[0]), int(item.split(",")[1])))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n")

    return output_path