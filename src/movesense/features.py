"""Trajectory kinematic and behavioural feature extraction module."""

import numpy as np
import pandas as pd


def extract_track_kinematics(track_df: pd.DataFrame, fps: int = 25) -> dict:
    """Extract physical kinematic metrics for a single pedestrian trajectory.

    Parameters
    ----------
    track_df : pd.DataFrame
        DataFrame sorted by frame containing a single pedestrian track
        with columns: frame, (id or track_id), x, y, w, h.
    fps : int, default 25
        Video frame rate for real-time physics scaling.

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

    # 1. Posição do centroide ao longo do tempo
    cx = (track_df["x"] + track_df["w"] / 2.0).to_numpy()
    cy = (track_df["y"] + track_df["h"] / 2.0).to_numpy()

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

    # 2. Deslocamentos euclidianos (pixels)
    dx = np.diff(cx)
    dy = np.diff(cy)
    step_distances = np.sqrt(dx**2 + dy**2)

    # 3. Velocidades instantâneas (pixels/segundo)
    speeds = step_distances * fps
    mean_speed = float(np.mean(speeds))
    max_speed = float(np.max(speeds))
    std_speed = float(np.std(speeds))

    # 4. Acelerações (pixels/segundo^2)
    if len(speeds) >= 2:
        accels = np.diff(speeds) * fps
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


def extract_trajectory_features(tracks_df: pd.DataFrame, fps: int = 25) -> pd.DataFrame:
    """Extract kinematic feature table for all pedestrians in a tracks DataFrame.

    Parameters
    ----------
    tracks_df : pd.DataFrame
        DataFrame of tracks with columns: frame, (id or track_id), x, y, w, h.
    fps : int, default 25
        Video frame rate.

    Returns
    -------
    pd.DataFrame
        Summary table with one row per unique track_id and kinematic columns.
    """
    id_col = "track_id" if "track_id" in tracks_df.columns else "id"
    records = []

    for _, group in tracks_df.groupby(id_col):
        sorted_group = group.sort_values(by="frame").reset_index(drop=True)
        metrics = extract_track_kinematics(sorted_group, fps=fps)
        records.append(metrics)

    return pd.DataFrame(records)