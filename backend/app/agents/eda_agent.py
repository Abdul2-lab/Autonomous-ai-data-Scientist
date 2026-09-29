"""
Agent 3 -- EDA Agent.
Real statistical analysis: distributions, correlations, relationships,
and findings derived from actual thresholds (not LLM guesswork).
"""
import pandas as pd
import numpy as np

from app.agents.base_agent import BaseAgent
from app.utils.helpers import clean_float


class EDAAgent(BaseAgent):
    name = "eda_agent"

    def run(self, df: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str]) -> dict:
        findings = []

        distributions = {}
        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty:
                continue
            skew = clean_float(series.skew())
            kurt = clean_float(series.kurtosis())
            distributions[col] = {"skewness": skew, "kurtosis": kurt}
            if skew is not None and abs(skew) > 1:
                direction = "right" if skew > 0 else "left"
                findings.append(f"Column '{col}' is strongly {direction}-skewed (skewness={skew:.2f}).")

        correlation_matrix = {}
        strong_correlations = []
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr(numeric_only=True)
            correlation_matrix = {
                c: {c2: clean_float(corr.loc[c, c2]) for c2 in numeric_cols} for c in numeric_cols
            }
            seen = set()
            for c1 in numeric_cols:
                for c2 in numeric_cols:
                    if c1 == c2 or (c2, c1) in seen:
                        continue
                    seen.add((c1, c2))
                    val = corr.loc[c1, c2]
                    if pd.notna(val) and abs(val) >= 0.7:
                        strong_correlations.append({"column_a": c1, "column_b": c2, "correlation": clean_float(val)})
            for sc in sorted(strong_correlations, key=lambda x: -abs(x["correlation"]))[:5]:
                findings.append(
                    f"Strong correlation ({sc['correlation']:.2f}) found between '{sc['column_a']}' and '{sc['column_b']}'."
                )

        categorical_findings = {}
        for col in categorical_cols:
            nunique = df[col].nunique(dropna=True)
            top = df[col].value_counts(dropna=True)
            categorical_findings[col] = {"unique_values": int(nunique)}
            if not top.empty:
                top_share = top.iloc[0] / top.sum()
                if top_share > 0.9:
                    findings.append(
                        f"Column '{col}' is dominated by a single value ('{top.index[0]}', {top_share*100:.1f}% of rows)."
                    )

        if not findings:
            findings.append("No strong skew, dominant categories, or highly correlated numeric pairs were detected.")

        return {
            "distributions": distributions,
            "correlation_matrix": correlation_matrix,
            "strong_correlations": strong_correlations,
            "categorical_findings": categorical_findings,
            "findings": findings,
        }
