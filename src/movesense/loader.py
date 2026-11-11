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
        usecols=range(9),
        index_col=False,
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

def load_mot_gt(
    file_path: pathlib.Path | str,
    valid_classes: tuple[int, ...] = (1,),
    active_only: bool = True,
    min_visibility: float = 0.0,
) -> pd.DataFrame:
    """Load a MOT ground-truth file filtered to valid pedestrian annotations.

    Parameters
    ----------
    file_path : pathlib.Path or str
        Path to the MOT ground-truth text file (e.g., gt/gt.txt).
    valid_classes : tuple[int, ...], default (1,)
        MOT class IDs to keep (class 1 = Pedestrian in MOTChallenge).
    active_only : bool, default True
        If True, discard rows marked with flag/conf == 0 (ignored regions).
    min_visibility : float, default 0.0
        Minimum visibility ratio (0.0 to 1.0) required to keep a box.

    Returns
    -------
    pd.DataFrame
        Filtered MOT ground-truth DataFrame sorted by frame and id.
    """
    df = load_mot_file(file_path)
    mask = df["class_id"].isin(valid_classes) & (df["visibility"] >= min_visibility)
    if active_only:
        mask &= df["conf"] >= 1.0
    return df.loc[mask].reset_index(drop=True)    