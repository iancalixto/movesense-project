"""Rule engine and scale normalization for MoveSense (DS-09).

Implements size-normalized kinematics (body lengths/s, v/h) to eliminate camera
perspective bias, posture classification via aspect ratio (w/h), and kinematic
event detection configured via JSON.
"""

from typing import Tuple
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

def normalize_by_size(
    df_track: pd.DataFrame,
    fps: float = 30.0,
    min_height_px: float = 15.0,
) -> pd.DataFrame:
    """Normalize trajectory velocity by bounding-box height."""
    df = df_track.copy().sort_values("frame").reset_index(drop=True)

    heights = df["h"].clip(lower=min_height_px)
    df["aspect_ratio"] = df["w"] / heights

    if len(df) < 2:
        df["speed_px_s"] = 0.0
        df["speed_bl_s"] = 0.0
        return df

    cx = df["x"] + df["w"] / 2.0
    cy = df["y"] + df["h"] / 2.0

    dt = np.diff(df["frame"]) / fps
    dt = np.where(dt <= 0.0, 1.0 / fps, dt)

    dx = np.diff(cx)
    dy = np.diff(cy)
    dist_px = np.sqrt(dx**2 + dy**2)
    speed_px_s = dist_px / dt

    h_pairs = (heights.values[:-1] + heights.values[1:]) / 2.0
    speed_bl_s = speed_px_s / h_pairs

    df["speed_px_s"] = np.concatenate([[speed_px_s[0]], speed_px_s])
    df["speed_bl_s"] = np.concatenate([[speed_bl_s[0]], speed_bl_s])

    return df


def detect_laydown(
    df_track: pd.DataFrame,
    min_aspect_ratio: float = 1.05,
) -> Tuple[bool, float]:
    """Detect laydown/kneeling posture based on bounding box aspect ratio (w/h)."""
    if "aspect_ratio" in df_track.columns:
        ar = df_track["aspect_ratio"]
    else:
        ar = df_track["w"] / df_track["h"].clip(lower=10.0)

    median_ar = float(ar.median())
    is_laydown = bool(median_ar >= min_aspect_ratio)
    return is_laydown, median_ar


def detect_sudden_stop(
    df_track: pd.DataFrame,
    initial_speed_min: float = 0.80,
    final_speed_max: float = 0.25,
    window_frames: int = 18,
) -> Tuple[bool, int]:
    """Detect sudden deceleration from moving to stationary within a short window."""
    if len(df_track) < 4:
        return False, -1

    speeds = df_track["speed_bl_s"].values
    frames = df_track["frame"].values
    n = len(speeds)

    w = min(window_frames, n)
    for i in range(w, n):
        past_speed = np.mean(speeds[max(0, i - w) : max(1, i - w // 2)])
        recent_speed = np.mean(speeds[i - w // 2 : i + 1])
        if past_speed >= initial_speed_min and recent_speed <= final_speed_max:
            return True, int(frames[i - w // 2])

    return False, -1


def detect_direction_change(
    df_track: pd.DataFrame,
    min_angle_deg: float = 85.0,
    min_speed_bl_s: float = 0.30,
    window_frames: int = 5,
) -> Tuple[bool, float]:
    """Detect sharp direction inversion (angle >= min_angle_deg) while moving."""
    if len(df_track) < window_frames * 2:
        return False, 0.0

    cx = (df_track["x"] + df_track["w"] / 2.0).values
    cy = (df_track["y"] + df_track["h"] / 2.0).values
    speeds = df_track["speed_bl_s"].values

    max_angle = 0.0
    w = window_frames
    for i in range(w, len(cx) - w):
        if speeds[i] < min_speed_bl_s:
            continue

        v1 = np.array([cx[i] - cx[i - w], cy[i] - cy[i - w]], dtype=np.float64)
        v2 = np.array([cx[i + w] - cx[i], cy[i + w] - cy[i]], dtype=np.float64)

        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 > 1e-3 and norm2 > 1e-3:
            cos_theta = np.dot(v1, v2) / (norm1 * norm2)
            cos_theta = np.clip(cos_theta, -1.0, 1.0)
            angle_deg = float(np.degrees(np.arccos(cos_theta)))
            if angle_deg > max_angle:
                max_angle = angle_deg

    has_changed = bool(max_angle >= min_angle_deg)
    return has_changed, max_angle


def detect_loitering(
    df_track: pd.DataFrame,
    max_radius_bl: float = 1.8,
    min_duration_s: float = 3.0,
    fps: float = 30.0,
) -> Tuple[bool, float, float]:
    """Detect loitering (staying confined in a small area for an extended period)."""
    if len(df_track) < 5:
        return False, 0.0, 0.0

    duration_s = float((df_track["frame"].max() - df_track["frame"].min() + 1) / fps)
    cx = (df_track["x"] + df_track["w"] / 2.0).values
    cy = (df_track["y"] + df_track["h"] / 2.0).values
    mean_h = float(df_track["h"].mean())
    if mean_h <= 0.0:
        mean_h = 50.0

    center_x = np.mean(cx)
    center_y = np.mean(cy)
    distances_px = np.sqrt((cx - center_x) ** 2 + (cy - center_y) ** 2)
    radius_bl = float(np.max(distances_px) / mean_h)

    is_loitering = bool(duration_s >= min_duration_s and radius_bl <= max_radius_bl)
    return is_loitering, radius_bl, duration_s

class RuleEngine:
    """Configurable rule engine evaluating pedestrian behaviors and anomalies."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @classmethod
    def from_config(cls, config_path: Union[str, Path]) -> "RuleEngine":
        """Load configuration from JSON file."""
        path = Path(config_path)
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cls(cfg)

    def evaluate_track(self, df_track: pd.DataFrame, fps: float = 30.0) -> Dict[str, Any]:
        """Evaluate a track and return primary behaviour and anomalies."""
        norm_cfg = self.config.get("scale_normalization", {})
        min_h = norm_cfg.get("min_height_px", 15.0)

        df_norm = normalize_by_size(df_track, fps=fps, min_height_px=min_h)

        # 1. Checagem de postura (queda / deitado)
        posture_cfg = self.config.get("posture", {})
        min_ar = posture_cfg.get("laydown_aspect_ratio_min", 1.05)
        is_laydown, median_ar = detect_laydown(df_norm, min_aspect_ratio=min_ar)

        # 2. Eventos cinemáticos e anomalias
        anomalies: List[str] = []

        stop_cfg = self.config.get("sudden_stop", {})
        has_stopped, stop_frame = detect_sudden_stop(
            df_norm,
            initial_speed_min=stop_cfg.get("initial_speed_min_bl_s", 0.80),
            final_speed_max=stop_cfg.get("final_speed_max_bl_s", 0.25),
            window_frames=int(stop_cfg.get("time_window_s", 0.6) * fps),
        )
        if has_stopped:
            anomalies.append(f"sudden_stop@frame_{stop_frame}")

        turn_cfg = self.config.get("direction_change", {})
        has_turned, max_angle = detect_direction_change(
            df_norm,
            min_angle_deg=turn_cfg.get("min_angle_degrees", 85.0),
            min_speed_bl_s=turn_cfg.get("min_speed_bl_s", 0.30),
            window_frames=turn_cfg.get("window_frames", 5),
        )
        if has_turned:
            anomalies.append(f"direction_change_{int(max_angle)}deg")

        # 3. Loitering (perambulação / vadiagem em raio restrito)
        loiter_cfg = self.config.get("loitering", {})
        is_loiter, conf_radius_bl, duration_s = detect_loitering(
            df_norm,
            max_radius_bl=loiter_cfg.get("max_confinement_radius_bl", 1.8),
            min_duration_s=loiter_cfg.get("min_duration_s", 3.0),
            fps=fps,
        )

        # 4. Hierarquia de classificacao comportamental da planilha
        speed_cfg = self.config.get("speed_thresholds_bl_per_s", {})
        standing_max = speed_cfg.get("standing_max", 0.30)
        walking_max = speed_cfg.get("walking_max", 1.45)

        mean_speed_bl = float(df_norm["speed_bl_s"].mean())

        if is_laydown:
            primary = "laydown/kneeling"
        elif is_loiter:
            primary = "loitering"
        elif mean_speed_bl <= standing_max:
            primary = "standing"
        elif mean_speed_bl <= walking_max:
            primary = "walking"
        else:
            primary = "running"

        return {
            "track_id": int(df_track["track_id"].iloc[0]) if "track_id" in df_track.columns else -1,
            "primary_behaviour": primary,
            "is_laydown": is_laydown,
            "median_aspect_ratio": round(median_ar, 3),
            "mean_speed_bl_s": round(mean_speed_bl, 3),
            "duration_s": round(duration_s, 2),
            "confinement_radius_bl": round(conf_radius_bl, 2),
            "anomalies": anomalies,
            "normalized_df": df_norm,
        }