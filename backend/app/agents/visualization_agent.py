"""
Agent 4 -- Visualization Agent.
Selects chart types based on actual column types and returns real computed
chart data (not styling) for the frontend to render.
"""
import numpy as np
import pandas as pd

from app.agents.base_agent import BaseAgent
from app.utils.helpers import clean_float


class VisualizationAgent(BaseAgent):
    name = "visualization_agent"
    MAX_SCATTER_POINTS = 500
    MAX_CHARTS = 12

    def run(self, df: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str],
            target_column: str | None = None) -> list[dict]:
        charts = []

        # Histograms for numeric columns
        for col in numeric_cols[:6]:
            series = df[col].dropna()
            if series.empty or series.nunique() <= 1:
                continue
            counts, bin_edges = np.histogram(series, bins=min(20, max(5, series.nunique())))
            charts.append({
                "type": "histogram",
                "title": f"Distribution of {col}",
                "column": col,
                "bins": [clean_float(b) for b in bin_edges],
                "counts": [int(c) for c in counts],
            })

        # Bar charts for categorical columns (low cardinality only -- meaningful charts)
        for col in categorical_cols:
            nunique = df[col].nunique(dropna=True)
            if nunique == 0 or nunique > 20:
                continue
            vc = df[col].value_counts(dropna=True).head(15)
            charts.append({
                "type": "bar",
                "title": f"Category counts: {col}",
                "column": col,
                "categories": [str(x) for x in vc.index.tolist()],
                "values": [int(v) for v in vc.values.tolist()],
            })

        # Correlation heatmap
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr(numeric_only=True)
            charts.append({
                "type": "heatmap",
                "title": "Correlation Heatmap",
                "columns": numeric_cols,
                "matrix": [[clean_float(v) for v in row] for row in corr.values],
            })

        # Box plots for numeric columns (outlier visualization)
        for col in numeric_cols[:4]:
            series = df[col].dropna()
            if series.empty:
                continue
            charts.append({
                "type": "boxplot",
                "title": f"Box plot: {col}",
                "column": col,
                "min": clean_float(series.min()),
                "q1": clean_float(series.quantile(0.25)),
                "median": clean_float(series.median()),
                "q3": clean_float(series.quantile(0.75)),
                "max": clean_float(series.max()),
            })

        # Scatter plot for the two most correlated numeric columns
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr(numeric_only=True).abs()
            corr_vals = corr.to_numpy(copy=True)
            np.fill_diagonal(corr_vals, 0)
            if corr_vals.size > 0:
                idx = np.unravel_index(np.argmax(corr_vals), corr_vals.shape)
                col_a, col_b = numeric_cols[idx[0]], numeric_cols[idx[1]]
                sample = df[[col_a, col_b]].dropna()
                if len(sample) > self.MAX_SCATTER_POINTS:
                    sample = sample.sample(self.MAX_SCATTER_POINTS, random_state=42)
                charts.append({
                    "type": "scatter",
                    "title": f"{col_a} vs {col_b}",
                    "x_column": col_a,
                    "y_column": col_b,
                    "points": [
                        {"x": clean_float(x), "y": clean_float(y)}
                        for x, y in zip(sample[col_a], sample[col_b])
                    ],
                })

        # Target distribution, if target provided
        if target_column and target_column in df.columns:
            if target_column in categorical_cols or df[target_column].nunique() <= 20:
                vc = df[target_column].value_counts(dropna=True)
                charts.append({
                    "type": "bar",
                    "title": f"Target distribution: {target_column}",
                    "column": target_column,
                    "categories": [str(x) for x in vc.index.tolist()],
                    "values": [int(v) for v in vc.values.tolist()],
                })

        return charts[: self.MAX_CHARTS]
