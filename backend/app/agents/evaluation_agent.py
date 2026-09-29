"""
Agent 8 -- Model Evaluation Agent.
Computes real metrics from actual predictions. Selects the metric used for
"best model" ranking based on problem characteristics, and documents that choice
rather than claiming one metric is universally best.
"""
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, mean_absolute_error, mean_squared_error, r2_score, roc_curve,
)

from app.agents.base_agent import BaseAgent
from app.utils.helpers import clean_float


class EvaluationAgent(BaseAgent):
    name = "evaluation_agent"

    def run(self, problem_type: str, y_true, y_pred, y_proba=None, class_labels=None) -> dict:
        if problem_type == "classification":
            return self._evaluate_classification(y_true, y_pred, y_proba, class_labels)
        elif problem_type == "regression":
            return self._evaluate_regression(y_true, y_pred)
        else:
            return {}

    def _evaluate_classification(self, y_true, y_pred, y_proba, class_labels) -> dict:
        n_classes = len(set(y_true))
        average = "binary" if n_classes == 2 else "macro"

        metrics = {
            "accuracy": clean_float(accuracy_score(y_true, y_pred)),
            "precision": clean_float(precision_score(y_true, y_pred, average=average, zero_division=0)),
            "recall": clean_float(recall_score(y_true, y_pred, average=average, zero_division=0)),
            "f1": clean_float(f1_score(y_true, y_pred, average=average, zero_division=0)),
            "primary_metric": "f1",
        }

        roc_auc = None
        if y_proba is not None and n_classes == 2:
            try:
                roc_auc = clean_float(roc_auc_score(y_true, y_proba[:, 1]))
            except Exception:
                roc_auc = None
        metrics["roc_auc"] = roc_auc

        # ROC curve points (binary only), downsampled so the payload stays small.
        metrics["roc_curve"] = None
        if y_proba is not None and n_classes == 2:
            try:
                pos_label = sorted(set(y_true))[1]
                fpr, tpr, _ = roc_curve(y_true, y_proba[:, 1], pos_label=pos_label)
                step = max(1, len(fpr) // 60)
                metrics["roc_curve"] = {
                    "fpr": [clean_float(v) for v in fpr[::step]] + [1.0],
                    "tpr": [clean_float(v) for v in tpr[::step]] + [1.0],
                }
            except Exception:
                metrics["roc_curve"] = None

        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = cm.tolist()
        metrics["confusion_matrix_labels"] = [str(c) for c in (class_labels if class_labels is not None else sorted(set(y_true)))]

        return metrics

    def _evaluate_regression(self, y_true, y_pred) -> dict:
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        return {
            "mae": clean_float(mae),
            "mse": clean_float(mse),
            "rmse": clean_float(rmse),
            "r2": clean_float(r2),
            "primary_metric": "r2",
        }
