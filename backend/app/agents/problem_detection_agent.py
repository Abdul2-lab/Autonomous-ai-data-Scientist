"""
Agent 5 -- ML Problem Detection Agent.
Uses statistical rules (not LLM guesswork) to decide classification vs
regression vs clustering vs unsuitable.
"""
import pandas as pd

from app.agents.base_agent import BaseAgent


class ProblemDetectionAgent(BaseAgent):
    name = "problem_detection_agent"

    MIN_ROWS_FOR_SUPERVISED = 20

    def run(self, df: pd.DataFrame, target_column: str | None,
            numeric_cols: list[str], categorical_cols: list[str]) -> dict:
        n_rows = len(df)

        if n_rows < self.MIN_ROWS_FOR_SUPERVISED:
            return {
                "problem_type": "unsuitable",
                "reason": f"Dataset has only {n_rows} rows; at least {self.MIN_ROWS_FOR_SUPERVISED} "
                          "are recommended for reliable supervised learning.",
                "target_column": target_column,
            }

        if not target_column or target_column not in df.columns:
            return {
                "problem_type": "clustering",
                "reason": "No target column was specified or found, so unsupervised clustering "
                          "is suggested instead of supervised learning.",
                "target_column": None,
            }

        target = df[target_column]
        nunique = target.nunique(dropna=True)
        non_null_ratio = target.notna().mean()

        if non_null_ratio < 0.5:
            return {
                "problem_type": "unsuitable",
                "reason": f"Target column '{target_column}' has too many missing values "
                          f"({(1-non_null_ratio)*100:.1f}%) to train a reliable model.",
                "target_column": target_column,
            }

        is_numeric = target_column in numeric_cols

        if not is_numeric:
            if nunique < 2:
                return {
                    "problem_type": "unsuitable",
                    "reason": f"Target column '{target_column}' has only one unique value.",
                    "target_column": target_column,
                }
            return {
                "problem_type": "classification",
                "reason": f"Target column '{target_column}' is categorical with {nunique} classes.",
                "target_column": target_column,
                "n_classes": int(nunique),
            }

        # Numeric target: decide classification vs regression by cardinality ratio
        ratio = nunique / n_rows
        if nunique <= 10 or ratio < 0.05:
            return {
                "problem_type": "classification",
                "reason": f"Target column '{target_column}' is numeric but has only {nunique} distinct "
                          "values relative to dataset size, indicating discrete classes.",
                "target_column": target_column,
                "n_classes": int(nunique),
            }

        return {
            "problem_type": "regression",
            "reason": f"Target column '{target_column}' is continuous numeric with {nunique} distinct values.",
            "target_column": target_column,
        }
