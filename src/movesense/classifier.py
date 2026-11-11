"""Pedestrian behaviour classification module using Random Forest."""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split

FEATURE_COLUMNS: list[str] = [
    "duration_frames",
    "mean_speed",
    "max_speed",
    "std_speed",
    "mean_acceleration",
    "confinement_radius",
]


class BehaviourClassifier:
    """Supervised classifier for pedestrian trajectory behaviours."""

    def __init__(self, n_estimators: int = 50, random_state: int = 42) -> None:
        """Initialize the Random Forest behaviour classifier.

        Parameters
        ----------
        n_estimators : int, default 50
            Number of decision trees in the Random Forest.
        random_state : int, default 42
            Seed for reproducible training and data splitting.
        """
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
        )
        self.is_trained = False
        self.classes_: list[str] = []

    def train(
        self,
        df: pd.DataFrame,
        target_col: str = "heuristic_label",
        test_size: float = 0.25,
    ) -> dict:
        """Train the classifier and return evaluation metrics on the test split.

        Parameters
        ----------
        df : pd.DataFrame
            Feature table containing FEATURE_COLUMNS and target_col.
        target_col : str, default 'heuristic_label'
            Name of the column holding ground-truth behaviour labels.
        test_size : float, default 0.25
            Fraction of data reserved for testing.

        Returns
        -------
        dict
            Evaluation metrics including accuracy, macro_f1, and report.
        """
        X = df[FEATURE_COLUMNS]
        y = df[target_col]

        # Usa estratificação se todas as classes tiverem amostras suficientes para dividir
        can_stratify = (
            y.value_counts().min() >= 2
            and int(len(df) * test_size) >= y.nunique()
        )
        stratify_arg = y if can_stratify else None

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=stratify_arg,
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True
        self.classes_ = [str(c) for c in self.model.classes_]

        y_pred = self.model.predict(X_test)
        acc = float(accuracy_score(y_test, y_pred))
        macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
        report = classification_report(y_test, y_pred, zero_division=0)

        return {
            "accuracy": acc,
            "macro_f1": macro_f1,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "classification_report": report,
        }

    def predict(self, df: pd.DataFrame) -> list[str]:
        """Predict behaviour labels for new trajectory feature rows."""
        if not self.is_trained:
            raise RuntimeError(
                "BehaviourClassifier must be trained before calling predict()."
            )

        X = df[FEATURE_COLUMNS]
        predictions = self.model.predict(X)
        return [str(p) for p in predictions]