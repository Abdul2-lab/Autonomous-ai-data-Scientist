import pandas as pd
import numpy as np
from app.agents.problem_detection_agent import ProblemDetectionAgent
from app.agents.model_selection_agent import ModelSelectionAgent
from app.agents.training_agent import TrainingAgent


def _make_classification_df(n=150):
    rng = np.random.default_rng(0)
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    y = (x1 + x2 > 0).astype(int)
    cat = rng.choice(["A", "B"], n)
    return pd.DataFrame({"x1": x1, "x2": x2, "cat": cat, "target": y})


def test_problem_detection_classification():
    df = _make_classification_df()
    result = ProblemDetectionAgent().run(df, "target", ["x1", "x2", "target"], ["cat"])
    assert result["problem_type"] == "classification"


def test_model_selection_returns_candidates():
    candidates = ModelSelectionAgent().run("classification", 150, 3)
    names = [c["name"] for c in candidates]
    assert "LogisticRegression" in names
    assert "RandomForestClassifier" in names


def test_training_agent_trains_and_picks_best(tmp_path):
    df = _make_classification_df()
    candidates = ModelSelectionAgent().run("classification", len(df), 3)
    result = TrainingAgent().run(
        df, "target", "classification", candidates,
        numeric_cols=["x1", "x2"], categorical_cols=["cat"], analysis_id=1,
    )
    assert result["best_model_name"] is not None
    successful = [e for e in result["experiments"] if e["status"] == "success"]
    assert len(successful) >= 1
    for exp in successful:
        assert exp["metrics"]["accuracy"] >= 0.0
    assert result["best_model_path"] is not None
    import os
    assert os.path.exists(result["best_model_path"])
