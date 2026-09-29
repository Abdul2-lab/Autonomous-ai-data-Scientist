"""
Agent 11 -- Report Agent.
Assembles all prior agent outputs into a structured 13-section report and
renders it to a standalone HTML file (no external services needed).
"""
import os
import html
import uuid
from datetime import datetime, timezone

from app.config import settings


SECTION_TITLES = [
    "Executive Summary", "Dataset Overview", "Data Quality", "Data Cleaning",
    "Exploratory Analysis", "Important Patterns", "Machine Learning",
    "Model Comparison", "Best Model", "Feature Importance", "AI Insights",
    "Limitations", "Suggested Next Steps",
]


class ReportAgent:
    name = "report_agent"

    def run(self, analysis_id: int, dataset_name: str, profiling: dict, quality: dict,
            cleaning: dict, eda: dict, ml_results: dict | None, explainability: dict | None,
            insights: dict) -> dict:

        sections = {
            "Executive Summary": insights.get("executive_summary") or "\n".join(insights.get("key_findings", [])[:3]),
            "Dataset Overview": {
                "rows": profiling.get("rows"), "columns": profiling.get("columns"),
                "numeric_columns": profiling.get("numeric_columns"),
                "categorical_columns": profiling.get("categorical_columns"),
                "memory_usage_mb": profiling.get("memory_usage_mb"),
            },
            "Data Quality": quality,
            "Data Cleaning": cleaning,
            "Exploratory Analysis": {"findings": eda.get("findings", [])},
            "Important Patterns": eda.get("strong_correlations", []),
            "Machine Learning": {
                "problem_type": ml_results.get("problem_type") if ml_results else None,
                "target_column": ml_results.get("target_column") if ml_results else None,
                "excluded_columns": ml_results.get("excluded_columns") if ml_results else None,
            },
            "Model Comparison": (
                ml_results.get("experiments") or
                (ml_results.get("clustering") or {}).get("k_scores", [])
            ) if ml_results else [],
            "Best Model": ml_results.get("best_model_name") if ml_results else None,
            "Feature Importance": explainability,
            "AI Insights": {
                "key_findings": insights.get("key_findings", []),
                "generated_by": insights.get("generated_by"),
            },
            "Limitations": insights.get("limitations", []),
            "Suggested Next Steps": insights.get("next_steps", []),
        }

        html_content = self._render_html(dataset_name, analysis_id, sections)

        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        filename = f"report_analysis_{analysis_id}_{uuid.uuid4().hex}.html"
        file_path = os.path.join(settings.REPORTS_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {"sections": sections, "file_path": file_path}

    def _render_html(self, dataset_name: str, analysis_id: int, sections: dict) -> str:
        def fmt(value):
            if isinstance(value, (dict, list)):
                return f"<pre>{html.escape(str(value))}</pre>"
            return f"<p>{html.escape(str(value))}</p>"

        body = "".join(
            f"<section><h2>{html.escape(title)}</h2>{fmt(sections.get(title))}</section>"
            for title in SECTION_TITLES
        )

        return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>AI Data Science Report - {html.escape(dataset_name)}</title>
<style>
body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 900px; margin: 40px auto; color: #1a1a1a; line-height: 1.5; }}
h1 {{ font-size: 1.8rem; }}
h2 {{ font-size: 1.2rem; margin-top: 2rem; border-bottom: 1px solid #ddd; padding-bottom: 6px; }}
pre {{ background: #f6f7f9; padding: 12px; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; }}
.meta {{ color: #666; font-size: 0.9rem; }}
</style></head>
<body>
<h1>AI Data Science Report</h1>
<p class="meta">Dataset: {html.escape(dataset_name)} &middot; Analysis ID: {analysis_id} &middot; Generated: {datetime.now(timezone.utc).isoformat()}</p>
{body}
</body></html>"""
