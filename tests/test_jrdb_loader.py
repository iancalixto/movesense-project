"""Unit tests for JackRabbot Dataset (JRDB) loader and parser (DE-09)."""

import json
from pathlib import Path
import pytest

from movesense.jrdb_loader import JRDBLoader


@pytest.fixture
def sample_jrdb_json(tmp_path: Path) -> Path:
    """Fixture providing a mock JRDB 2D stitched labels file."""
    data = {
        "labels": {
            "000001.jpg": [
                {
                    "box": [100.0, 150.0, 50.0, 120.0],
                    "label_id": "pedestrian:1",
                    "action": "walking"
                },
                {
                    "box": [250.0, 300.0, 120.0, 80.0],
                    "label_id": "pedestrian:2",
                    "action": "kneeling"
                }
            ],
            "000002.jpg": [
                {
                    "box": [105.0, 150.0, 50.0, 120.0],
                    "label_id": "pedestrian:1",
                    "action": "walking"
                }
            ]
        }
    }
    json_path = tmp_path / "sample_jrdb_labels.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    return json_path


def test_parse_jrdb_json_to_dataframe(sample_jrdb_json: Path):
    """Verify that JRDBLoader parses Stanford JSON into a standardized DataFrame."""
    loader = JRDBLoader(mapping_config_path="configs/jrdb_action_mapping.json")
    df = loader.load_labels(sample_jrdb_json)

    # 1. Checa schema e quantidade de linhas (2 no frame 1 + 1 no frame 2 = 3)
    assert len(df) == 3
    expected_cols = {"frame", "track_id", "x", "y", "w", "h", "raw_action", "action"}
    assert expected_cols.issubset(set(df.columns))

    # 2. Checa extracao correta de frame e track_id
    ped1 = df[df["track_id"] == 1]
    assert len(ped1) == 2
    assert list(ped1["frame"]) == [1, 2]

    # 3. Checa traducao de acoes
    ped2 = df[df["track_id"] == 2].iloc[0]
    assert ped2["raw_action"] == "kneeling"
    assert ped2["action"] == "laydown/kneeling"


def test_jrdb_missing_file_raises_error():
    """Verify that attempting to load a non-existent file raises FileNotFoundError."""
    loader = JRDBLoader(mapping_config_path="configs/jrdb_action_mapping.json")
    with pytest.raises(FileNotFoundError):
        loader.load_labels("caminho/inexistente/labels.json")