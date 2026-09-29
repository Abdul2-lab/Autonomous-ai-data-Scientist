"""
Shared helpers: loading dataframes safely, and making analysis results JSON-serializable
(numpy/pandas types are not natively JSON serializable).
"""
import json
import numpy as np
import pandas as pd

from app.core.exceptions import AppError


def load_dataframe(path: str, ext: str) -> pd.DataFrame:
    try:
        if ext == ".csv":
            df = pd.read_csv(path)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(path)
        else:
            raise AppError(f"Unsupported file extension: {ext}")
    except pd.errors.EmptyDataError:
        raise AppError("The uploaded file has no readable data.")
    except pd.errors.ParserError:
        raise AppError("The uploaded CSV could not be parsed. It may be corrupted or malformed.")
    except ValueError as e:
        raise AppError(f"The uploaded Excel file could not be read: {e}")

    if df.shape[0] == 0:
        raise AppError("The dataset contains no rows.")
    if df.shape[1] == 0:
        raise AppError("The dataset contains no columns.")

    return df


class NumpySafeEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy/pandas scalar types."""

    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        if isinstance(obj, (pd.Timestamp,)):
            return obj.isoformat()
        if pd.isna(obj) if not isinstance(obj, (list, dict)) else False:
            return None
        return super().default(obj)


def to_json_safe(data) -> str:
    return json.dumps(data, cls=NumpySafeEncoder)


def from_json_safe(text: str | None):
    if not text:
        return None
    return json.loads(text)


def clean_float(value) -> float | None:
    """Convert a numpy/py float to a JSON-safe python float, or None if NaN/inf."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(f) or np.isinf(f):
        return None
    return f


def get_categorical_columns(df: pd.DataFrame) -> list[str]:
    """Non-numeric, non-datetime columns. Robust across pandas 2.x/3.x string dtypes."""
    numeric = set(df.select_dtypes(include=[np.number]).columns)
    return [
        c for c in df.columns
        if c not in numeric and not pd.api.types.is_datetime64_any_dtype(df[c])
    ]


def identifier_like_columns(df: pd.DataFrame, high_cardinality: list[str] | None = None) -> list[str]:
    """Columns that identify rows (IDs) rather than describe them. They carry no
    generalisable signal, so they are excluded from ML features and clustering."""
    excluded = set(high_cardinality or [])
    n = len(df)
    id_names = {"id", "custid", "customerid", "userid", "orderid", "rowid", "recordid"}
    for c in df.columns:
        name = str(c).strip().lower()
        looks_like_id = name in id_names or name.endswith("_id") or name.endswith(" id")
        if looks_like_id and n > 0 and df[c].nunique(dropna=True) >= 0.9 * n:
            excluded.add(c)
    return [c for c in df.columns if c in excluded]
