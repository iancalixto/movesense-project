"""Automated downloader for MOT20 extreme density pedestrian benchmark sequence (MOT20-01)."""

import os
from pathlib import Path
from huggingface_hub import snapshot_download


def download_mot20_sequence(seq_name: str = "MOT20-01") -> Path:
    """Download single MOT20 sequence from Hugging Face dataset mirror.

    Parameters
    ----------
    seq_name : str
        Target sequence folder (e.g. 'MOT20-01').

    Returns
    -------
    Path
        Directory containing the downloaded sequence.
    """
    target_dir = Path("data/MOT20")
    target_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f"DOWNLOADING MOT20 EXTREME CROWD BENCHMARK ({seq_name})")
    print("Mirror: Hugging Face (Lekim89/MOT20)")
    print(f"Destination: {target_dir.resolve()}")
    print("=" * 80)

    # Download only the targeted sequence to optimize bandwidth and disk space
    pattern = f"train/{seq_name}/*"
    downloaded_path = snapshot_download(
        repo_id="Lekim89/MOT20",
        repo_type="dataset",
        allow_patterns=pattern,
        local_dir=str(target_dir),
    )

    seq_path = target_dir / "train" / seq_name
    print(f"\n[OK] Sequence downloaded successfully: {seq_path}")

    # Verify extracted structure
    img_dir = seq_path / "img1"
    gt_file = seq_path / "gt" / "gt.txt"

    if img_dir.exists():
        frames = list(img_dir.glob("*.jpg"))
        print(f"[VERIFIED] Found {len(frames)} frames in img1 directory.")
    if gt_file.exists():
        print(f"[VERIFIED] Ground truth annotations found: {gt_file}")

    return seq_path


if __name__ == "__main__":
    download_mot20_sequence("MOT20-01")