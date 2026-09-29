"""
Agent 6 -- ML Model Selection Agent.
Chooses candidate models based on problem type AND dataset characteristics
(size), rather than blindly training every algorithm.
"""
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor,
    HistGradientBoostingClassifier, HistGradientBoostingRegressor,
)
from sklearn.svm import SVC
from sklearn.cluster import KMeans

from app.agents.base_agent import BaseAgent

SVM_ROW_LIMIT = 5000  # SVM does not scale well; skip on large datasets


class ModelSelectionAgent(BaseAgent):
    name = "model_selection_agent"

    def run(self, problem_type: str, n_rows: int, n_features: int) -> list[dict]:
        candidates = []

        if problem_type == "classification":
            candidates.append({"name": "LogisticRegression", "estimator": LogisticRegression(max_iter=1000)})
            candidates.append({"name": "DecisionTreeClassifier", "estimator": DecisionTreeClassifier(random_state=42)})
            candidates.append({"name": "RandomForestClassifier", "estimator": RandomForestClassifier(n_estimators=200, random_state=42)})
            candidates.append({"name": "GradientBoostingClassifier", "estimator": GradientBoostingClassifier(random_state=42)})
            candidates.append({"name": "HistGradientBoostingClassifier", "estimator": HistGradientBoostingClassifier(random_state=42)})
            if n_rows <= SVM_ROW_LIMIT:
                candidates.append({"name": "SVC", "estimator": SVC(probability=True, random_state=42)})

        elif problem_type == "regression":
            candidates.append({"name": "LinearRegression", "estimator": LinearRegression()})
            candidates.append({"name": "Ridge", "estimator": Ridge()})
            candidates.append({"name": "DecisionTreeRegressor", "estimator": DecisionTreeRegressor(random_state=42)})
            candidates.append({"name": "RandomForestRegressor", "estimator": RandomForestRegressor(n_estimators=200, random_state=42)})
            candidates.append({"name": "GradientBoostingRegressor", "estimator": GradientBoostingRegressor(random_state=42)})
            candidates.append({"name": "HistGradientBoostingRegressor", "estimator": HistGradientBoostingRegressor(random_state=42)})

        elif problem_type == "clustering":
            k = min(8, max(2, n_rows // 50)) if n_rows > 0 else 2
            candidates.append({"name": f"KMeans(k={k})", "estimator": KMeans(n_clusters=k, random_state=42, n_init=10)})

        return candidates
