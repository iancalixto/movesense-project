"""Loader and parser for JackRabbot Dataset and Benchmark (JRDB) 2D annotations (DE-09).

Converts Stanford JRDB-Act JSON annotations into standardized MoveSense DataFrames
and maps robotics action labels to MoveSense behavioural categories.
"""

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Union
import pandas as pd


class JRDBLoader:
    """Loader for JRDB 2D bounding boxes and spatio-temporal action annotations."""

    def __init__(
        self,
        mapping_config_path: Union[str, Path] = "configs/jrdb_action_mapping.json",
    ) -> None:
        """Initialize loader with action category mapping."""
        self.mapping_path = Path(mapping_config_path)
        self.mapping: Dict[str, str] = {}
        self.default_action: str = "unknown"

        if self.mapping_path.exists():
            with open(self.mapping_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                self.mapping = cfg.get("mapping", {})
                self.default_action = cfg.get("default_action", "unknown")

    def map_action(self, raw_action: str) -> str:
        """Translate a JRDB action label to MoveSense taxonomy."""
        cleaned = str(raw_action).strip().lower()
        return self.mapping.get(cleaned, self.default_action)

    def load_labels(self, json_path: Union[str, Path]) -> pd.DataFrame:
        """Load and parse a JRDB 2D label JSON file.

        Parameters
        ----------
        json_path : Union[str, Path]
            Path to the JRDB JSON file (e.g., labels_2d_stitched).

        Returns
        -------
        pd.DataFrame
            DataFrame with columns:
            ['frame', 'track_id', 'x', 'y', 'w', 'h', 'raw_action', 'action']
        """
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"JRDB label file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        labels_dict = data.get("labels", {})
        records: List[Dict[str, Any]] = []

        for img_name, detections in labels_dict.items():
            # Extrai o numero do frame a partir do nome do arquivo (ex: '000001.jpg' -> 1)
            frame_digits = re.findall(r"\d+", Path(img_name).stem)
            frame_idx = int(frame_digits[-1]) if frame_digits else 1

            for det in detections:
                box = det.get("box", [0.0, 0.0, 0.0, 0.0])
                label_id_str = str(det.get("label_id", "pedestrian:0"))

                # Extrai o ID numerico (ex: 'pedestrian:1' -> 1)
                id_digits = re.findall(r"\d+", label_id_str)
                track_id = int(id_digits[-1]) if id_digits else 0

                raw_action = det.get("action", det.get("attributes", {}).get("action", "unknown"))
                action = self.map_action(raw_action)

                records.append({
                    "frame": frame_idx,
                    "track_id": track_id,
                    "x": float(box[0]),
                    "y": float(box[1]),
                    "w": float(box[2]),
                    "h": float(box[3]),
                    "raw_action": str(raw_action),
                    "action": action,
                })

        df = pd.DataFrame(records)
        if df.empty:
            return pd.DataFrame(
                columns=["frame", "track_id", "x", "y", "w", "h", "raw_action", "action"]
            )

        return df.sort_values(by=["frame", "track_id"]).reset_index(drop=True)