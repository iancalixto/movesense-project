"""Render full synthetic video from the generated gt.txt dataset.

Run:
    python scripts/render_video.py
"""

import pathlib
from movesense.render import render_synthetic_video


def main() -> None:
    gt_file = pathlib.Path("data/synthetic/gt.txt")
    output_video = pathlib.Path("data/synthetic/synthetic_video.avi")

    if not gt_file.exists():
        raise FileNotFoundError(
            f"Ground-truth file not found at {gt_file}. Run 'make step-02' first to generate it!"
        )

    print(f"Reading annotations from: {gt_file}")
    print("Rendering synthetic video (this takes ~1-2 seconds)...")

    render_synthetic_video(
        gt_path=gt_file,
        output_video_path=output_video,
        img_w=1920,
        img_h=1080,
        fps=25,
    )

    print(f"Video successfully rendered at: {output_video}")


if __name__ == "__main__":
    main()