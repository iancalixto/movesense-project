"""Loader for standard MOT (Multiple Object Tracking) format files."""

import pathlib
import pandas as pd

# The canonical 9 columns defined in MOTChallenge benchmark
MOT_COLUMNS: list[str] = [
    "frame",
    "id",
    "x",
    "y",
    "w",
    "h",
    "conf",
    "class_id",
    "visibility",
]


def load_mot_file(file_path: pathlib.Path | str) -> pd.DataFrame:
    """Load a MOT-formatted ground-truth or tracking detection file.

    Parameters
    ----------
    file_path : pathlib.Path or str
        Path to the MOT formatted text file (.txt).

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized MOT columns and typed fields.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    path = pathlib.Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"MOT file not found: {path}")

    df = pd.read_csv(
        path,
        header=None,
        names=MOT_COLUMNS,
        dtype={
            "frame": int,
            "id": int,
            "x": float,
            "y": float,
            "w": float,
            "h": float,
            "conf": float,
            "class_id": int,
            "visibility": float,
        },
    )

    return df.sort_values(by=["frame", "id"]).reset_index(drop=True)