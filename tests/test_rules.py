"""Unit tests for behaviour rules engine and scale normalization (DS-09)."""

import numpy as np
import pandas as pd
import pytest

from movesense.rules import (
    detect_direction_change,
    detect_laydown,
    detect_loitering,
    detect_sudden_stop,
    normalize_by_size,
)


def test_scale_normalization_perspective_invariance():
    """Verify that scale normalization by height (v/h) makes near and far pedestrians comparable."""
    fps = 30.0

    # Pedestre 1: Perto da camera (altura h=300px), andando a 300 px/s (10 px/frame)
    frames = list(range(1, 31))
    df_close = pd.DataFrame({
        "frame": frames,
        "track_id": 1,
        "x": [100.0 + i * 10.0 for i in range(30)],
        "y": [500.0] * 30,
        "w": [120.0] * 30,
        "h": [300.0] * 30,
    })

    # Pedestre 2: Longe no fundo (altura h=60px), andando a 60 px/s (2 px/frame)
    df_far = pd.DataFrame({
        "frame": frames,
        "track_id": 2,
        "x": [400.0 + i * 2.0 for i in range(30)],
        "y": [100.0] * 30,
        "w": [24.0] * 30,
        "h": [60.0] * 30,
    })

    df_norm_close = normalize_by_size(df_close, fps=fps)
    df_norm_far = normalize_by_size(df_far, fps=fps)

    mean_speed_close = df_norm_close["speed_bl_s"].mean()
    mean_speed_far = df_norm_far["speed_bl_s"].mean()

    assert np.isclose(mean_speed_close, 1.0, atol=0.05)
    assert np.isclose(mean_speed_far, 1.0, atol=0.05)


def test_posture_laydown_detection():
    """Verify laydown/kneeling detection when aspect ratio w/h >= 1.05."""
    df_laydown = pd.DataFrame({
        "frame": list(range(1, 21)),
        "track_id": 3,
        "x": [200.0] * 20,
        "y": [300.0] * 20,
        "w": [150.0] * 20,
        "h": [90.0] * 20,
    })
    df_standing = pd.DataFrame({
        "frame": list(range(1, 21)),
        "track_id": 4,
        "x": [100.0] * 20,
        "y": [300.0] * 20,
        "w": [50.0] * 20,
        "h": [140.0] * 20,
    })

    is_laydown_pos, aspect_ratio_pos = detect_laydown(df_laydown, min_aspect_ratio=1.05)
    is_laydown_neg, aspect_ratio_neg = detect_laydown(df_standing, min_aspect_ratio=1.05)

    assert is_laydown_pos is True
    assert aspect_ratio_pos >= 1.05
    assert is_laydown_neg is False
    assert aspect_ratio_neg < 0.6


def test_sudden_stop_rule():
    """Verify sudden stop detection when track rapidly decelerates from fast to static."""
    fps = 30.0
    h = 100.0
    # Primeiros 15 frames: movimento rapido (12 px/frame = 360 px/s = 3.6 bl/s)
    # Proximos 15 frames: estatico subito (0 px/frame)
    x = [i * 12.0 for i in range(15)] + [14 * 12.0] * 15
    df_stop = pd.DataFrame({
        "frame": list(range(1, 31)),
        "track_id": 5,
        "x": x,
        "y": [200.0] * 30,
        "w": [40.0] * 30,
        "h": [h] * 30,
    })
    df_stop = normalize_by_size(df_stop, fps=fps)

    has_stopped, stop_frame = detect_sudden_stop(
        df_stop,
        initial_speed_min=0.8,
        final_speed_max=0.25,
        window_frames=18,
    )

    assert has_stopped is True
    assert 13 <= stop_frame <= 18


def test_direction_change_rule():
    """Verify sharp direction change detection (turn >= 85 degrees while moving)."""
    fps = 30.0
    h = 100.0
    # 10 frames para a direita (+x), depois 10 frames para baixo (+y) -> curva de 90 graus!
    x = [100.0 + i * 5.0 for i in range(10)] + [145.0] * 10
    y = [200.0] * 10 + [200.0 + i * 5.0 for i in range(10)]
    df_turn = pd.DataFrame({
        "frame": list(range(1, 21)),
        "track_id": 6,
        "x": x,
        "y": y,
        "w": [40.0] * 20,
        "h": [h] * 20,
    })
    df_turn = normalize_by_size(df_turn, fps=fps)

    has_changed, max_angle = detect_direction_change(
        df_turn,
        min_angle_deg=85.0,
        min_speed_bl_s=0.3,
        window_frames=5,
    )

    assert has_changed is True
    assert max_angle >= 85.0


def test_loitering_rule():
    """Verify loitering detection (track stays confined within small radius for >= duration)."""
    fps = 30.0
    h = 100.0
    # 120 frames (4 segundos a 30fps) andando em circulos pequenos (raio 15px = 0.15 corpo)
    angles = np.linspace(0, 4 * np.pi, 120)
    x = 200.0 + 15.0 * np.cos(angles)
    y = 200.0 + 15.0 * np.sin(angles)

    df_loiter = pd.DataFrame({
        "frame": list(range(1, 121)),
        "track_id": 7,
        "x": x,
        "y": y,
        "w": [40.0] * 120,
        "h": [h] * 120,
    })
    df_loiter = normalize_by_size(df_loiter, fps=fps)

    is_loitering, confinement_radius_bl, duration_s = detect_loitering(
        df_loiter,
        max_radius_bl=1.8,
        min_duration_s=3.0,
        fps=fps,
    )

    assert is_loitering is True
    assert confinement_radius_bl < 1.0
    assert duration_s >= 3.0

from pathlib import Path
from movesense.rules import RuleEngine


@pytest.fixture
def default_rules_config(tmp_path: Path) -> Path:
    """Fixture providing a temporary rules config file."""
    import json
    config = {
        "scale_normalization": {"min_height_px": 15.0},
        "posture": {"laydown_aspect_ratio_min": 1.05},
        "speed_thresholds_bl_per_s": {
            "standing_max": 0.30,
            "walking_max": 1.45,
            "running_min": 1.45
        },
        "sudden_stop": {
            "initial_speed_min_bl_s": 0.80,
            "final_speed_max_bl_s": 0.25,
            "time_window_s": 0.60
        },
        "direction_change": {
            "min_angle_degrees": 85.0,
            "min_speed_bl_s": 0.30,
            "window_frames": 5
        },
        "loitering": {
            "max_confinement_radius_bl": 1.8,
            "min_duration_s": 3.0
        }
    }
    cfg_file = tmp_path / "behaviour_rules.json"
    with open(cfg_file, "w") as f:
        json.dump(config, f)
    return cfg_file


def test_rule_engine_integration(default_rules_config: Path):
    """Verify RuleEngine loading from config and classifying behaviour."""
    engine = RuleEngine.from_config(default_rules_config)

    # 1. Pedestre caminhando normalmente (90 px/s com h=100px -> 0.9 corpos/s)
    h = 100.0
    df_walk = pd.DataFrame({
        "frame": list(range(1, 31)),
        "track_id": 10,
        "x": [100.0 + i * 3.0 for i in range(30)],
        "y": [200.0] * 30,
        "w": [40.0] * 30,
        "h": [h] * 30,
    })
    result_walk = engine.evaluate_track(df_walk, fps=30.0)
    assert result_walk["primary_behaviour"] == "walking"
    assert result_walk["is_laydown"] is False

    # 2. Pedestre deitado no chao (w=140, h=70 -> w/h = 2.0)
    df_fall = pd.DataFrame({
        "frame": list(range(1, 31)),
        "track_id": 11,
        "x": [100.0] * 30,
        "y": [200.0] * 30,
        "w": [140.0] * 30,
        "h": [70.0] * 30,
    })
    result_fall = engine.evaluate_track(df_fall, fps=30.0)
    assert result_fall["primary_behaviour"] == "laydown/kneeling"
    assert result_fall["is_laydown"] is True

from pathlib import Path
from movesense.rules import RuleEngine


@pytest.fixture
def default_rules_config(tmp_path: Path) -> Path:
    """Fixture providing a temporary rules config file."""
    import json
    config = {
        "scale_normalization": {"min_height_px": 15.0},
        "posture": {"laydown_aspect_ratio_min": 1.05},
        "speed_thresholds_bl_per_s": {
            "standing_max": 0.30,
            "walking_max": 1.45,
            "running_min": 1.45
        },
        "sudden_stop": {
            "initial_speed_min_bl_s": 0.80,
            "final_speed_max_bl_s": 0.25,
            "time_window_s": 0.60
        },
        "direction_change": {
            "min_angle_degrees": 85.0,
            "min_speed_bl_s": 0.30,
            "window_frames": 5
        },
        "loitering": {
            "max_confinement_radius_bl": 1.8,
            "min_duration_s": 3.0
        }
    }
    cfg_file = tmp_path / "behaviour_rules.json"
    with open(cfg_file, "w") as f:
        json.dump(config, f)
    return cfg_file


def test_rule_engine_integration(default_rules_config: Path):
    """Verify RuleEngine loading from config and classifying behaviour."""
    engine = RuleEngine.from_config(default_rules_config)

    # 1. Pedestre caminhando normalmente (90 px/s com h=100px -> 0.9 corpos/s)
    h = 100.0
    df_walk = pd.DataFrame({
        "frame": list(range(1, 31)),
        "track_id": 10,
        "x": [100.0 + i * 3.0 for i in range(30)],
        "y": [200.0] * 30,
        "w": [40.0] * 30,
        "h": [h] * 30,
    })
    result_walk = engine.evaluate_track(df_walk, fps=30.0)
    assert result_walk["primary_behaviour"] == "walking"
    assert result_walk["is_laydown"] is False

    # 2. Pedestre deitado no chao (w=140, h=70 -> w/h = 2.0)
    df_fall = pd.DataFrame({
        "frame": list(range(1, 31)),
        "track_id": 11,
        "x": [100.0] * 30,
        "y": [200.0] * 30,
        "w": [140.0] * 30,
        "h": [70.0] * 30,
    })
    result_fall = engine.evaluate_track(df_fall, fps=30.0)
    assert result_fall["primary_behaviour"] == "laydown/kneeling"
    assert result_fall["is_laydown"] is True