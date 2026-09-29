"""
Agent 2 -- Data Cleaning Agent.
Never modifies the original uploaded file. Produces a cleaned copy plus a
summary of exactly what was changed and why.
"""
import os
import uuid
import pandas as pd
import numpy as np

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.utils.helpers import get_categorical_columns


class CleaningAgent(BaseAgent):
    name = "cleaning_agent"

    def run(self, df: pd.DataFrame, profiling: dict) -> tuple[pd.DataFrame, dict, str]:
        original_shape = df.shape
        cleaned = df.copy()
        actions = []

        # 1. Drop exact duplicate rows
        dup_count = int(cleaned.duplicated().sum())
        if dup_count > 0:
            cleaned = cleaned.drop_duplicates()
            actions.append(f"Removed {dup_count} exact duplicate row(s).")

        numeric_cols = cleaned.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = [c for c in get_categorical_columns(cleaned) if cleaned[c].dtype != bool]

        # 2. Attempt numeric-string conversion for object columns that are actually numeric
        converted_numeric = []
        for col in list(categorical_cols):
            coerced = pd.to_numeric(cleaned[col], errors="coerce")
            non_null_original = cleaned[col].notna().sum()
            if non_null_original > 0 and coerced.notna().sum() / non_null_original > 0.95:
                cleaned[col] = coerced
                converted_numeric.append(col)
                categorical_cols.remove(col)
                numeric_cols.append(col)
        if converted_numeric:
            actions.append(f"Converted columns to numeric type: {converted_numeric}.")

        # 3. Handle missing values
        missing_before = int(cleaned.isnull().sum().sum())
        imputed_numeric, imputed_categorical = [], []
        for col in numeric_cols:
            if cleaned[col].isnull().any():
                median_val = cleaned[col].median()
                cleaned[col] = cleaned[col].fillna(median_val)
                imputed_numeric.append(col)
        for col in categorical_cols:
            if cleaned[col].isnull().any():
                mode_series = cleaned[col].mode(dropna=True)
                fill_val = mode_series.iloc[0] if not mode_series.empty else "Unknown"
                cleaned[col] = cleaned[col].fillna(fill_val)
                imputed_categorical.append(col)
        if imputed_numeric:
            actions.append(f"Filled missing numeric values with column median in: {imputed_numeric}.")
        if imputed_categorical:
            actions.append(f"Filled missing categorical values with column mode in: {imputed_categorical}.")

        # 4. Outlier detection (IQR method) -- reported, not removed automatically
        outlier_report = {}
        for col in numeric_cols:
            q1, q3 = cleaned[col].quantile(0.25), cleaned[col].quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            n_outliers = int(((cleaned[col] < lower) | (cleaned[col] > upper)).sum())
            if n_outliers > 0:
                outlier_report[col] = {
                    "count": n_outliers,
                    "percentage": round(n_outliers / len(cleaned) * 100, 2),
                    "lower_bound": float(lower),
                    "upper_bound": float(upper),
                }
        if outlier_report:
            actions.append(
                f"Detected potential outliers (IQR method) in {len(outlier_report)} column(s); "
                "not removed automatically, flagged for review."
            )

        # 5. Drop constant columns (zero information for ML) -- reported, not silently hidden
        constant_cols = [c for c in cleaned.columns if cleaned[c].nunique(dropna=True) <= 1]

        missing_after = int(cleaned.isnull().sum().sum())

        # Save processed copy -- never overwrite the original.
        os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
        processed_filename = f"{uuid.uuid4().hex}_cleaned.csv"
        processed_path = os.path.join(settings.PROCESSED_DIR, processed_filename)
        cleaned.to_csv(processed_path, index=False)

        summary = {
            "original_rows": original_shape[0],
            "original_columns": original_shape[1],
            "cleaned_rows": cleaned.shape[0],
            "cleaned_columns": cleaned.shape[1],
            "duplicate_rows_removed": dup_count,
            "columns_converted_to_numeric": converted_numeric,
            "missing_values_before": missing_before,
            "missing_values_after": missing_after,
            "numeric_columns_imputed": imputed_numeric,
            "categorical_columns_imputed": imputed_categorical,
            "outlier_report": outlier_report,
            "constant_columns_detected": constant_cols,
            "actions_taken": actions if actions else ["No cleaning actions were necessary; dataset was already clean."],
            "processed_file_path": processed_path,
        }

        return cleaned, summary, processed_path
