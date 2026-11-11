"""Tests for pedestrian behaviour classification module using Scikit-Learn."""

import pandas as pd
import pytest
from movesense.classifier import BehaviourClassifier


@pytest.fixture
def sample_training_data() -> pd.DataFrame:
    """Generate synthetic feature samples for the 4 behaviour classes."""
    data = []
    # 5 amostras de standing: velocidade=0, confinamento=0
    for i in range(5):
        data.append({
            "track_id": i + 1,
            "duration_frames": 20 + i,
            "mean_speed": 0.0,
            "max_speed": 0.0,
            "std_speed": 0.0,
            "mean_acceleration": 0.0,
            "confinement_radius": 0.0,
            "label": "standing",
        })
    # 5 amostras de loitering: vel baixa (15-30), raio pequeno (2-10)
    for i in range(5):
        data.append({
            "track_id": i + 6,
            "duration_frames": 30 + i,
            "mean_speed": 20.0 + i,
            "max_speed": 35.0,
            "std_speed": 5.0,
            "mean_acceleration": 2.0,
            "confinement_radius": 5.0 + i,
            "label": "loitering",
        })
    # 5 amostras de walking: vel moderada (90-130), raio médio (200-250)
    for i in range(5):
        data.append({
            "track_id": i + 11,
            "duration_frames": 50 + i,
            "mean_speed": 100.0 + i * 5,
            "max_speed": 135.0,
            "std_speed": 10.0,
            "mean_acceleration": 5.0,
            "confinement_radius": 200.0 + i * 10,
            "label": "walking",
        })
    # 5 amostras de running: vel alta (>700), raio grande (>600)
    for i in range(5):
        data.append({
            "track_id": i + 16,
            "duration_frames": 40 + i,
            "mean_speed": 800.0 + i * 50,
            "max_speed": 1200.0,
            "std_speed": 80.0,
            "mean_acceleration": 40.0,
            "confinement_radius": 700.0 + i * 20,
            "label": "running",
        })

    return pd.DataFrame(data)


def test_classifier_trains_and_evaluates(sample_training_data: pd.DataFrame):
    """Verify BehaviourClassifier trains and outputs evaluation metrics."""
    clf = BehaviourClassifier(n_estimators=30, random_state=42)

    metrics = clf.train(sample_training_data, target_col="label", test_size=0.25)

    assert clf.is_trained is True
    assert "accuracy" in metrics
    assert "macro_f1" in metrics
    assert metrics["accuracy"] >= 0.80


def test_classifier_predict_single_instance(sample_training_data: pd.DataFrame):
    """Verify trained classifier makes accurate predictions for standing and running."""
    clf = BehaviourClassifier(n_estimators=30, random_state=42)
    clf.train(sample_training_data, target_col="label", test_size=0.25)

    # Novo pedestre estático
    test_static = pd.DataFrame([{
        "duration_frames": 15,
        "mean_speed": 0.0,
        "max_speed": 0.0,
        "std_speed": 0.0,
        "mean_acceleration": 0.0,
        "confinement_radius": 0.0,
    }])
    assert clf.predict(test_static)[0] == "standing"

    # Novo pedestre correndo
    test_runner = pd.DataFrame([{
        "duration_frames": 35,
        "mean_speed": 950.0,
        "max_speed": 1300.0,
        "std_speed": 75.0,
        "mean_acceleration": 50.0,
        "confinement_radius": 800.0,
    }])
    assert clf.predict(test_runner)[0] == "running"


def test_classifier_predict_before_training_raises():
    """Verify calling predict() before train() raises a clear RuntimeError."""
    clf = BehaviourClassifier()
    dummy_df = pd.DataFrame([{
        "duration_frames": 10,
        "mean_speed": 0.0,
        "max_speed": 0.0,
        "std_speed": 0.0,
        "mean_acceleration": 0.0,
        "confinement_radius": 0.0,
    }])
    with pytest.raises(RuntimeError):
        clf.predict(dummy_df)