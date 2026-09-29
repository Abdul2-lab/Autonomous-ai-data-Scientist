"""
Agent 7 -- Model Training Agent.
Builds leakage-safe sklearn Pipelines (preprocessing fit only on train fold),
trains each candidate model, cross-validates, evaluates on a held-out test
set, and persists the best model with joblib.
"""
import os
import uuid
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
import joblib

from app.agents.base_agent import BaseAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.config import settings


class TrainingAgent(BaseAgent):
    name = "training_agent"

    def run(self, df: pd.DataFrame, target_column: str, problem_type: str,
            candidates: list[dict], numeric_cols: list[str], categorical_cols: list[str],
            analysis_id: int) -> dict:

        feature_numeric = [c for c in numeric_cols if c != target_column]
        feature_categorical = [c for c in categorical_cols if c != target_column]

        data = df.dropna(subset=[target_column]).copy()
        X = data[feature_numeric + feature_categorical]
        y = data[target_column]

        label_encoder = None
        class_labels = None
        if problem_type == "classification" and y.dtype == object:
            label_encoder = LabelEncoder()
            y = label_encoder.fit_transform(y.astype(str))
            class_labels = label_encoder.classes_.tolist()
        elif problem_type == "classification":
            class_labels = sorted(pd.Series(y).unique().tolist())

        stratify = y if problem_type == "classification" and pd.Series(y).nunique() > 1 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=stratify
        )

        preprocessor = ColumnTransformer(transformers=[
            ("numeric", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), feature_numeric),
            ("categorical", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]), feature_categorical),
        ])

        evaluator = EvaluationAgent()
        experiments = []
        best = None

        for cand in candidates:
            model_name = cand["name"]
            estimator = cand["estimator"]
            pipe = Pipeline([("preprocessor", preprocessor), ("model", estimator)])

            try:
                pipe.fit(X_train, y_train)
                y_pred = pipe.predict(X_test)
                y_proba = None
                if problem_type == "classification" and hasattr(pipe, "predict_proba"):
                    try:
                        y_proba = pipe.predict_proba(X_test)
                    except Exception:
                        y_proba = None

                metrics = evaluator.run(problem_type, y_test, y_pred, y_proba, class_labels)

                cv_scores = None
                try:
                    scoring = "f1_macro" if problem_type == "classification" else "r2"
                    cv = cross_val_score(pipe, X_train, y_train, cv=min(5, max(2, len(X_train) // 20)), scoring=scoring)
                    cv_scores = {"mean": float(np.mean(cv)), "std": float(np.std(cv)), "scoring": scoring}
                except Exception:
                    cv_scores = None

                primary_metric = metrics.get("primary_metric")
                primary_value = metrics.get(primary_metric) if primary_metric else None

                experiment = {
                    "model_name": model_name,
                    "metrics": metrics,
                    "cross_validation": cv_scores,
                    "primary_metric_value": primary_value,
                    "status": "success",
                }
                experiments.append((experiment, pipe))

                if primary_value is not None and (best is None or primary_value > best[0]["primary_metric_value"]):
                    best = experiment, pipe

            except Exception as e:
                experiments.append(({
                    "model_name": model_name,
                    "status": "failed",
                    "error": str(e),
                }, None))

        best_model_path = None
        if best is not None:
            os.makedirs(settings.MODELS_DIR, exist_ok=True)
            best_model_path = os.path.join(settings.MODELS_DIR, f"analysis_{analysis_id}_{uuid.uuid4().hex}.joblib")
            joblib.dump({
                "pipeline": best[1],
                "feature_columns": feature_numeric + feature_categorical,
                "label_encoder": label_encoder,
                "class_labels": class_labels,
                "problem_type": problem_type,
            }, best_model_path)
            best[0]["model_path"] = best_model_path
            best[0]["is_best"] = True

        # Small sample of held-out features for the explainability agent (SHAP needs real X rows).
        explain_sample = X_test.head(min(100, len(X_test))) if best is not None else None

        return {
            "problem_type": problem_type,
            "target_column": target_column,
            "feature_columns": feature_numeric + feature_categorical,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "experiments": [e for e, _ in experiments],
            "best_model_name": best[0]["model_name"] if best else None,
            "best_model_path": best_model_path,
            "class_labels": class_labels,
            "_explain_sample": explain_sample,  # not persisted to DB; used in-process only
        }
