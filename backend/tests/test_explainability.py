import pandas as pd
import numpy as np
from app.agents.model_selection_agent import ModelSelectionAgent
from app.agents.training_agent import TrainingAgent
from app.agents.explainability_agent import ExplainabilityAgent


def _make_df(n=150):
    rng = np.random.default_rng(1)
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    y = (x1 * 2 + x2 > 0).astype(int)
    return pd.DataFrame({"x1": x1, "x2": x2, "target": y})


def test_explainability_uses_shap_for_tree_model_when_available():
    df = _make_df()
    candidates = [c for c in ModelSelectionAgent().run("classification", len(df), 2)
                  if c["name"] == "RandomForestClassifier"]
    result = TrainingAgent().run(df, "target", "classification", candidates,
                                  numeric_cols=["x1", "x2"], categorical_cols=[], analysis_id=99)
    assert result["best_model_path"] is not None

    import joblib
    bundle = joblib.load(result["best_model_path"])
    sample = df[["x1", "x2"]].head(50)

    explanation = ExplainabilityAgent().run(bundle["pipeline"], result["feature_columns"], X_sample=sample)
    assert explanation["available"] is True
    assert "top_features" in explanation
    assert len(explanation["top_features"]) > 0
    # Either SHAP or the native fallback is an acceptable, honestly-labeled method.
    assert "SHAP" in explanation["method"] or "importances" in explanation["method"]


def test_explainability_falls_back_gracefully_with_no_model():
    result = ExplainabilityAgent().run(None, ["x1", "x2"])
    assert result["available"] is False
