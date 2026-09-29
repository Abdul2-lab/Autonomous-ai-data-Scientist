"""
Agent 9 -- Explainability Agent.
Extracts real feature-importance / coefficient information from the trained
model. When SHAP is installed and practical for the selected model type, it
is used for more accurate, per-feature attribution; otherwise this falls
back to the model's native feature_importances_/coef_. Either way the
numbers come from the real trained model -- nothing is invented, and the
agent honestly reports when neither method is available.
"""
import logging
import numpy as np

from app.agents.base_agent import BaseAgent
from app.utils.helpers import clean_float

logger = logging.getLogger("app")

# Model families SHAP's fast TreeExplainer supports well; anything else
# falls back to native importances rather than paying SHAP's slower KernelExplainer cost.
_SHAP_TREE_MODELS = (
    "RandomForestClassifier", "RandomForestRegressor",
    "GradientBoostingClassifier", "GradientBoostingRegressor",
    "HistGradientBoostingClassifier", "HistGradientBoostingRegressor",
    "DecisionTreeClassifier", "DecisionTreeRegressor",
)


class ExplainabilityAgent(BaseAgent):
    name = "explainability_agent"

    def run(self, pipeline, feature_columns: list[str], X_sample=None) -> dict:
        if pipeline is None:
            return {"available": False, "reason": "No successfully trained model was available to explain."}

        model = pipeline.named_steps.get("model")
        preprocessor = pipeline.named_steps.get("preprocessor")
        model_type = type(model).__name__

        try:
            output_features = preprocessor.get_feature_names_out()
        except Exception:
            output_features = np.array(feature_columns)

        shap_result = None
        if X_sample is not None and model_type in _SHAP_TREE_MODELS:
            shap_result = self._try_shap(pipeline, model, preprocessor, output_features, X_sample)
        if shap_result is not None:
            return shap_result

        return self._native_importance(model, output_features, model_type)

    def _try_shap(self, pipeline, model, preprocessor, output_features, X_sample) -> dict | None:
        try:
            import shap  # optional dependency -- native importances are used if this import fails
            transformed = preprocessor.transform(X_sample)
            if hasattr(transformed, "toarray"):
                transformed = transformed.toarray()
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(transformed)

            # Classification returns a list of per-class arrays; use class 1 (or the first) for ranking.
            if isinstance(shap_values, list):
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]

            mean_abs = np.abs(shap_values).mean(axis=0)
            if len(mean_abs) != len(output_features):
                output_features = output_features[: len(mean_abs)]

            ranked = sorted(zip(output_features, mean_abs), key=lambda x: -abs(x[1]))[:15]
            return {
                "available": True,
                "method": "SHAP (TreeExplainer, mean |SHAP value|)",
                "top_features": [{"feature": str(f), "importance": clean_float(v)} for f, v in ranked],
                "limitations": (
                    "SHAP values quantify each feature's contribution to this model's predictions on "
                    "the sample data, not proven real-world causation. Correlated features may share "
                    "attributed importance."
                ),
            }
        except Exception as e:
            logger.info("SHAP explainability unavailable, falling back to native importances: %s", e)
            return None

    def _native_importance(self, model, output_features, model_type) -> dict:
        importances = None
        method = None

        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            method = "impurity-based feature_importances_"
        elif hasattr(model, "coef_"):
            coef = model.coef_
            importances = np.abs(coef[0]) if coef.ndim > 1 else np.abs(coef)
            method = "absolute coefficient magnitude"

        if importances is None:
            return {
                "available": False,
                "reason": f"Model type '{model_type}' does not expose feature importances, "
                          "coefficients, or a supported SHAP explainer.",
            }

        if len(importances) != len(output_features):
            output_features = output_features[: len(importances)]

        ranked = sorted(zip(output_features, importances), key=lambda x: -abs(x[1]))[:15]

        return {
            "available": True,
            "method": method,
            "top_features": [{"feature": str(f), "importance": clean_float(v)} for f, v in ranked],
            "limitations": (
                "Feature importance reflects the trained model's internal logic, not proven "
                "causation. Correlated features may share or dilute importance scores."
            ),
        }
