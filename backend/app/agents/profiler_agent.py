"""
Agent 1 -- Dataset Profiler.
Inspects the dataset and produces schema, dtypes, statistics, missing values,
duplicates, and candidate target columns. Pure pandas/numpy -- no LLM.
"""
import pandas as pd
import numpy as np

from app.agents.base_agent import BaseAgent
from app.utils.helpers import clean_float, get_categorical_columns


class ProfilerAgent(BaseAgent):
    name = "profiler_agent"

    def run(self, df: pd.DataFrame) -> dict:
        n_rows, n_cols = df.shape

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = get_categorical_columns(df)
        datetime_cols = self._detect_datetime_columns(df, categorical_cols)
        # datetime columns detected from object columns shouldn't double count as categorical
        categorical_cols = [c for c in categorical_cols if c not in datetime_cols]

        missing = df.isnull().sum()
        missing_pct = (missing / n_rows * 100).round(2)

        duplicate_rows = int(df.duplicated().sum())
        duplicate_columns = self._find_duplicate_columns(df)
        constant_columns = [c for c in df.columns if df[c].nunique(dropna=True) <= 1]
        high_cardinality = [
            c for c in categorical_cols
            if df[c].nunique(dropna=True) > max(50, int(0.5 * n_rows))
        ]

        dtypes = {c: str(df[c].dtype) for c in df.columns}

        numeric_summary = {}
        if numeric_cols:
            desc = df[numeric_cols].describe().to_dict()
            for col, stats in desc.items():
                numeric_summary[col] = {k: clean_float(v) for k, v in stats.items()}

        categorical_summary = {}
        for col in categorical_cols:
            vc = df[col].value_counts(dropna=True).head(10)
            categorical_summary[col] = {str(k): int(v) for k, v in vc.items()}

        candidate_targets = self._detect_candidate_targets(df, numeric_cols, categorical_cols, n_rows)

        memory_usage_mb = clean_float(df.memory_usage(deep=True).sum() / (1024 * 1024))

        return {
            "rows": n_rows,
            "columns": n_cols,
            "dtypes": dtypes,
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "datetime_columns": datetime_cols,
            "missing_values": {c: int(missing[c]) for c in df.columns},
            "missing_percentage": {c: clean_float(missing_pct[c]) for c in df.columns},
            "duplicate_rows": duplicate_rows,
            "duplicate_columns": duplicate_columns,
            "constant_columns": constant_columns,
            "high_cardinality_columns": high_cardinality,
            "numeric_summary": numeric_summary,
            "categorical_summary": categorical_summary,
            "candidate_target_columns": candidate_targets,
            "memory_usage_mb": memory_usage_mb,
        }

    @staticmethod
    def _detect_datetime_columns(df: pd.DataFrame, candidate_cols: list[str]) -> list[str]:
        detected = []
        for col in candidate_cols:
            sample = df[col].dropna().astype(str).head(30)
            if sample.empty:
                continue
            parsed = pd.to_datetime(sample, errors="coerce", format=None)
            if parsed.notna().mean() > 0.8:
                detected.append(col)
        return detected

    @staticmethod
    def _find_duplicate_columns(df: pd.DataFrame) -> list[list[str]]:
        groups: dict[str, list[str]] = {}
        for col in df.columns:
            try:
                key = pd.util.hash_pandas_object(df[col], index=False).sum()
            except TypeError:
                continue
            groups.setdefault(str(key), []).append(col)
        return [g for g in groups.values() if len(g) > 1]

    @staticmethod
    def _detect_candidate_targets(df, numeric_cols, categorical_cols, n_rows) -> list[dict]:
        candidates = []
        for col in categorical_cols:
            nunique = df[col].nunique(dropna=True)
            if 2 <= nunique <= 20:
                candidates.append({"column": col, "reason": "low-cardinality categorical (classification)", "unique_values": int(nunique)})
        for col in numeric_cols:
            nunique = df[col].nunique(dropna=True)
            if nunique <= 10 and n_rows > 0 and nunique / n_rows < 0.05:
                candidates.append({"column": col, "reason": "low-cardinality numeric (possible classification)", "unique_values": int(nunique)})
            elif nunique > 10:
                candidates.append({"column": col, "reason": "continuous numeric (possible regression)", "unique_values": int(nunique)})
        return candidates
