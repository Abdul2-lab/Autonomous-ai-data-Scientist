"""
Safe "tools" the chat feature calls to fetch grounded facts about an analysis.
The LLM is NEVER given raw code-execution access -- it only receives the
structured facts these functions return, and is instructed not to invent
anything beyond them.
"""
from typing import Any


def get_dataset_summary(context: dict) -> dict:
    profiling = context.get("profiling") or {}
    return {
        "rows": profiling.get("rows"),
        "columns": profiling.get("columns"),
        "numeric_columns": profiling.get("numeric_columns"),
        "categorical_columns": profiling.get("categorical_columns"),
        "datetime_columns": profiling.get("datetime_columns"),
    }


def get_column_statistics(context: dict, column: str) -> dict:
    profiling = context.get("profiling") or {}
    if column in (profiling.get("numeric_summary") or {}):
        return profiling["numeric_summary"][column]
    if column in (profiling.get("categorical_summary") or {}):
        return profiling["categorical_summary"][column]
    return {"error": f"No statistics available for column '{column}'."}


def get_missing_values(context: dict) -> dict:
    profiling = context.get("profiling") or {}
    return {
        "missing_values": profiling.get("missing_values"),
        "missing_percentage": profiling.get("missing_percentage"),
    }


def get_unique_values(context: dict, column: str) -> dict:
    profiling = context.get("profiling") or {}
    cat_summary = profiling.get("categorical_summary") or {}
    if column in cat_summary:
        return {"top_values": cat_summary[column]}
    return {"error": f"No categorical breakdown available for column '{column}'."}


def calculate_correlation(context: dict) -> dict:
    eda = context.get("eda") or {}
    return {"strong_correlations": eda.get("strong_correlations", [])}


def generate_chart(context: dict, chart_type: str | None = None) -> dict:
    charts = context.get("visualizations") or []
    if chart_type:
        charts = [c for c in charts if c.get("type") == chart_type]
    return {"available_charts": [{"type": c.get("type"), "title": c.get("title")} for c in charts]}


def _compact_clustering(c: dict | None) -> dict | None:
    """Clustering facts for the LLM without the bulky plotting points."""
    if not c:
        return None
    return {k: v for k, v in c.items() if k not in ("pca_points", "model_path")}


def get_model_results(context: dict) -> dict:
    ml = context.get("ml_results") or {}
    return {
        "problem_type": ml.get("problem_type"),
        "best_model_name": ml.get("best_model_name"),
        "excluded_columns": ml.get("excluded_columns"),
        "clustering": _compact_clustering(ml.get("clustering")),
        "experiments": [
            {"model_name": e.get("model_name"),
             "metrics": {k: v for k, v in (e.get("metrics") or {}).items() if k != "roc_curve"},
             "status": e.get("status")}
            for e in ml.get("experiments", [])
        ],
    }


def get_feature_importance(context: dict) -> dict:
    return context.get("explainability") or {"available": False}


def get_analysis_summary(context: dict) -> dict:
    return {
        "profiling": get_dataset_summary(context),
        "quality_findings": (context.get("quality") or {}).get("findings", []),
        "eda_findings": (context.get("eda") or {}).get("findings", []),
        "cleaning_actions": (context.get("cleaning") or {}).get("actions_taken", []),
        "outliers": (context.get("cleaning") or {}).get("outlier_report", {}),
        "strong_correlations": (context.get("eda") or {}).get("strong_correlations", []),
        "model_results": get_model_results(context),
        "feature_importance": get_feature_importance(context),
        "insights": context.get("insights"),
    }


TOOL_REGISTRY = {
    "get_dataset_summary": get_dataset_summary,
    "get_column_statistics": get_column_statistics,
    "get_missing_values": get_missing_values,
    "get_unique_values": get_unique_values,
    "calculate_correlation": calculate_correlation,
    "generate_chart": generate_chart,
    "get_model_results": get_model_results,
    "get_feature_importance": get_feature_importance,
    "get_analysis_summary": get_analysis_summary,
}
