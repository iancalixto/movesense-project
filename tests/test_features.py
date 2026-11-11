"""Tests for trajectory kinematic features extraction module."""

import numpy as np
import pandas as pd
import pytest
from movesense.features import (
    extract_track_kinematics,
    extract_trajectory_features,
    smooth_trajectory,
)


def test_extract_track_kinematics_constant_velocity():
    """Verify kinematics for a pedestrian walking at constant velocity."""
    # Pedestre se move 10 pixels por frame em X a 25 FPS -> velocidade = 250 px/s
    track_df = pd.DataFrame({
        "frame": [1, 2, 3, 4, 5],
        "id": [1, 1, 1, 1, 1],
        "x": [100.0, 110.0, 120.0, 130.0, 140.0],
        "y": [200.0, 200.0, 200.0, 200.0, 200.0],
        "w": [50.0, 50.0, 50.0, 50.0, 50.0],
        "h": [100.0, 100.0, 100.0, 100.0, 100.0],
    })

    metrics = extract_track_kinematics(track_df, fps=25)

    assert metrics["track_id"] == 1
    assert metrics["duration_frames"] == 5
    assert metrics["mean_speed"] == pytest.approx(250.0, rel=1e-2)
    assert metrics["mean_acceleration"] == pytest.approx(0.0, abs=1e-2)
    assert metrics["confinement_radius"] == pytest.approx(40.0, rel=1e-2)


def test_extract_track_kinematics_static_pedestrian():
    """Verify that a stationary pedestrian has 0 speed and 0 confinement radius."""
    track_df = pd.DataFrame({
        "frame": [1, 2, 3, 4],
        "id": [2, 2, 2, 2],
        "x": [300.0, 300.0, 300.0, 300.0],
        "y": [400.0, 400.0, 400.0, 400.0],
        "w": [50.0, 50.0, 50.0, 50.0],
        "h": [100.0, 100.0, 100.0, 100.0],
    })

    metrics = extract_track_kinematics(track_df, fps=25)

    assert metrics["track_id"] == 2
    assert metrics["mean_speed"] == 0.0
    assert metrics["max_speed"] == 0.0
    assert metrics["confinement_radius"] == 0.0


def test_extract_trajectory_features_full_dataframe():
    """Verify feature table extraction across multiple pedestrians."""
    tracks_df = pd.DataFrame({
        "frame": [1, 2, 1, 2],
        "id": [1, 1, 2, 2],
        "x": [10.0, 20.0, 50.0, 50.0],
        "y": [10.0, 10.0, 50.0, 50.0],
        "w": [30.0, 30.0, 30.0, 30.0],
        "h": [60.0, 60.0, 60.0, 60.0],
    })

    features_df = extract_trajectory_features(tracks_df, fps=25)

    assert isinstance(features_df, pd.DataFrame)
    assert len(features_df) == 2  # Dois pedestres únicos
    assert set(features_df["track_id"]) == {1, 2}
    assert "mean_speed" in features_df.columns
    assert "max_speed" in features_df.columns
    assert "confinement_radius" in features_df.columns


def test_smooth_trajectory_reduces_jitter_and_preserves_line():
    """Verify smoothing suppresses high-frequency jitter without distorting linear motion."""
    linear = np.linspace(100.0, 250.0, 31)
    assert np.allclose(smooth_trajectory(linear, window=9), linear)

    rng = np.random.default_rng(2026)
    noisy = linear + rng.normal(0.0, 5.0, size=len(linear))
    smoothed = smooth_trajectory(noisy, window=9)

    raw_step_std = np.std(np.diff(noisy))
    smooth_step_std = np.std(np.diff(smoothed))
    assert smooth_step_std < raw_step_std * 0.3


def test_extract_features_smoothing_and_min_frames_filter():
    """Verify min_frames drops short fragments and smooth_window dampens max_speed."""
    rng = np.random.default_rng(2026)
    n_frames = 35
    x_walk = 100.0 + np.arange(n_frames) * 5.0 + rng.normal(0.0, 5.0, size=n_frames)

    long_track = pd.DataFrame({
        "frame": np.arange(1, n_frames + 1),
        "id": 1,
        "x": x_walk,
        "y": 200.0,
        "w": 50.0,
        "h": 120.0,
    })
    short_noise = pd.DataFrame({
        "frame": [1, 2],
        "id": 2,
        "x": [50.0, 51.0],
        "y": [50.0, 50.0],
        "w": [40.0, 40.0],
        "h": [90.0, 90.0],
    })
    tracks_df = pd.concat([long_track, short_noise], ignore_index=True)

    raw_df = extract_trajectory_features(tracks_df, fps=25, smooth_window=1, min_frames=1)
    clean_df = extract_trajectory_features(tracks_df, fps=25, smooth_window=9, min_frames=5)

    assert len(raw_df) == 2
    assert len(clean_df) == 1
    assert int(clean_df.iloc[0]["track_id"]) == 1
    assert clean_df.iloc[0]["max_speed"] < raw_df.loc[raw_df["track_id"] == 1, "max_speed"].iloc[0] * 0.5