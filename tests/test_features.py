"""Tests for trajectory kinematic features extraction module."""

import pandas as pd
import pytest
from movesense.features import extract_trajectory_features, extract_track_kinematics


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