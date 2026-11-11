"""Trajectory kinematic and behavioural feature extraction module."""

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

FEATURE_DF_COLUMNS: list[str] = [
    "track_id",
    "duration_frames",
    "mean_speed",
    "max_speed",
    "std_speed",
    "mean_acceleration",
    "confinement_radius",
]


def smooth_trajectory(coords: np.ndarray, window: int = 9) -> np.ndarray:
    """Smooth a 1D coordinate sequence using a linear Savitzky-Golay filter.

    Uses polyorder=1 so constant-velocity straight lines are preserved without
    edge distortion while suppressing high-frequency frame-to-frame jitter.
    """
    arr = np.asarray(coords, dtype=float)
    if window <= 2 or len(arr) < 3:
        return arr.copy()

    win = min(int(window), len(arr))
    if win % 2 == 0:
        win -= 1
    if win < 3:
        return arr.copy()

    return savgol_filter(arr, window_length=win, polyorder=1)


def extract_track_kinematics(
    track_df: pd.DataFrame,
    fps: int = 25,
    smooth_window: int = 1,
) -> dict:
    """Extract physical kinematic metrics for a single pedestrian trajectory.

    Parameters
    ----------
    track_df : pd.DataFrame
        DataFrame sorted by frame containing a single pedestrian track
        with columns: frame, (id or track_id), x, y, w, h.
    fps : int, default 25
        Video frame rate for real-time physics scaling.
    smooth_window : int, default 1
        Temporal smoothing window length (>= 3 enables Savitzky-Golay smoothing).

    Returns
    -------
    dict
        Dictionary containing aggregated kinematic metrics.
    """
    if track_df.empty:
        raise ValueError("Cannot extract kinematics from empty track DataFrame.")

    # Suporta tanto a coluna 'id' quanto 'track_id'
    id_col = "track_id" if "track_id" in track_df.columns else "id"
    track_id = int(track_df[id_col].iloc[0])
    duration_frames = len(track_df)

    # 1. Posição do centroide ao longo do tempo (opcionalmente suavizada)
    cx = smooth_trajectory((track_df["x"] + track_df["w"] / 2.0).to_numpy(), window=smooth_window)
    cy = smooth_trajectory((track_df["y"] + track_df["h"] / 2.0).to_numpy(), window=smooth_window)

    if duration_frames < 2:
        return {
            "track_id": track_id,
            "duration_frames": duration_frames,
            "mean_speed": 0.0,
            "max_speed": 0.0,
            "std_speed": 0.0,
            "mean_acceleration": 0.0,
            "confinement_radius": 0.0,
        }

    # 2. Deslocamentos euclidianos divididos pelo delta real de frames (evita picos após falhas)
    frames = track_df["frame"].to_numpy()
    dt = np.maximum(np.diff(frames), 1)
    dx = np.diff(cx)
    dy = np.diff(cy)
    step_distances = np.sqrt(dx**2 + dy**2)

    # 3. Velocidades instantâneas (pixels/segundo)
    speeds = (step_distances / dt) * fps
    mean_speed = float(np.mean(speeds))
    max_speed = float(np.max(speeds))
    std_speed = float(np.std(speeds))

    # 4. Acelerações (pixels/segundo^2)
    if len(speeds) >= 2:
        accels = (np.diff(speeds) / dt[1:]) * fps
        mean_accel = float(np.mean(accels))
    else:
        mean_accel = 0.0

    # 5. Raio de confinamento espacial (distância máxima ao ponto inicial)
    dist_from_start = np.sqrt((cx - cx[0]) ** 2 + (cy - cy[0]) ** 2)
    confinement_radius = float(np.max(dist_from_start))

    return {
        "track_id": track_id,
        "duration_frames": duration_frames,
        "mean_speed": mean_speed,
        "max_speed": max_speed,
        "std_speed": std_speed,
        "mean_acceleration": mean_accel,
        "confinement_radius": confinement_radius,
    }


def extract_trajectory_features(
    tracks_df: pd.DataFrame,
    fps: int = 25,
    smooth_window: int = 1,
    min_frames: int = 1,
) -> pd.DataFrame:
    """Extract kinematic feature table for all pedestrians in a tracks DataFrame.

    Parameters
    ----------
    tracks_df : pd.DataFrame
        DataFrame of tracks with columns: frame, (id or track_id), x, y, w, h.
    fps : int, default 25
        Video frame rate.
    smooth_window : int, default 1
        Temporal smoothing window length (>= 3 enables Savitzky-Golay smoothing).
    min_frames : int, default 1
        Minimum number of detections required for a track to be retained.

    Returns
    -------
    pd.DataFrame
        Summary table with one row per valid unique track_id and kinematic columns.
    """
    if tracks_df.empty:
        return pd.DataFrame(columns=FEATURE_DF_COLUMNS)

    id_col = "track_id" if "track_id" in tracks_df.columns else "id"
    records = []

    for _, group in tracks_df.groupby(id_col):
        if len(group) < min_frames:
            continue
        sorted_group = group.sort_values(by="frame").reset_index(drop=True)
        metrics = extract_track_kinematics(sorted_group, fps=fps, smooth_window=smooth_window)
        records.append(metrics)

    return pd.DataFrame(records) if records else pd.DataFrame(columns=FEATURE_DF_COLUMNS)