"""
Central orchestrator. Runs every agent in sequence, persisting real progress
and real intermediate results to the Analysis row after each stage so the
frontend can poll and display genuine (not fake) progress.
"""
import logging
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.analysis import Analysis
from app.models.model_experiment import ModelExperiment
from datetime import datetime, timezone
from app.utils.helpers import load_dataframe, to_json_safe, from_json_safe, identifier_like_columns

from app.agents.profiler_agent import ProfilerAgent
from app.agents.cleaning_agent import CleaningAgent
from app.agents.eda_agent import EDAAgent
from app.agents.visualization_agent import VisualizationAgent
from app.agents.problem_detection_agent import ProblemDetectionAgent
from app.agents.model_selection_agent import ModelSelectionAgent
from app.agents.training_agent import TrainingAgent
from app.agents.clustering_agent import ClusteringAgent
from app.agents.explainability_agent import ExplainabilityAgent
from app.agents.insight_agent import InsightAgent
from app.agents.report_agent import ReportAgent
from app.models.report import Report

logger = logging.getLogger("app")

STAGES = [
    "profiling", "data_quality", "cleaning", "problem_detection", "eda",
    "visualization", "model_selection", "training", "evaluation",
    "explainability", "insight_generation", "report_generation", "completed",
]


class AnalysisPipeline:
    def __init__(self, db: Session):
        self.db = db

    def _set_stage(self, analysis: Analysis, stage: str, status: str = "running"):
        analysis.current_stage = stage
        analysis.status = status
        self.db.commit()

    def run_full_pipeline(self, analysis_id: int, target_column: str | None):
        analysis = self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis is None:
            logger.error("Analysis %s not found for pipeline run.", analysis_id)
            return

        dataset = self.db.query(Dataset).filter(Dataset.id == analysis.dataset_id).first()

        try:
            df = load_dataframe(dataset.stored_path, dataset.file_extension)

            # 1. Profiling
            self._set_stage(analysis, "profiling")
            profiler = ProfilerAgent()
            profiling = profiler.run(df)
            analysis.profiling_json = to_json_safe(profiling)
            self.db.commit()

            # 2. Data quality findings (derived from profiling; real thresholds)
            self._set_stage(analysis, "data_quality")
            quality = self._derive_quality_findings(profiling)
            analysis.quality_json = to_json_safe(quality)
            self.db.commit()

            # 3. Cleaning
            self._set_stage(analysis, "cleaning")
            cleaner = CleaningAgent()
            cleaned_df, cleaning_summary, _ = cleaner.run(df, profiling)
            analysis.cleaning_json = to_json_safe(cleaning_summary)
            self.db.commit()

            numeric_cols = [c for c in profiling["numeric_columns"] if c in cleaned_df.columns]
            categorical_cols = [c for c in profiling["categorical_columns"] if c in cleaned_df.columns]

            # ID-like / very high-cardinality columns identify rows rather than describe them.
            # They are kept for EDA but excluded from ML features and clustering.
            excluded_cols = identifier_like_columns(cleaned_df, profiling.get("high_cardinality_columns"))
            excluded_cols = [c for c in excluded_cols if c != target_column]
            ml_numeric_cols = [c for c in numeric_cols if c not in excluded_cols]
            ml_categorical_cols = [c for c in categorical_cols if c not in excluded_cols]

            # 4. Problem detection
            self._set_stage(analysis, "problem_detection")
            detector = ProblemDetectionAgent()
            problem_info = detector.run(cleaned_df, target_column, numeric_cols, categorical_cols)
            analysis.problem_type = problem_info["problem_type"]
            analysis.target_column = problem_info.get("target_column")
            self.db.commit()

            # 5. EDA
            self._set_stage(analysis, "eda")
            eda_agent = EDAAgent()
            eda_results = eda_agent.run(cleaned_df, numeric_cols, categorical_cols)
            analysis.eda_json = to_json_safe(eda_results)
            self.db.commit()

            # 6. Visualization
            self._set_stage(analysis, "visualization")
            viz_agent = VisualizationAgent()
            charts = viz_agent.run(cleaned_df, numeric_cols, categorical_cols, analysis.target_column)
            analysis.visualization_json = to_json_safe(charts)
            self.db.commit()

            ml_results = None
            explainability = {"available": False, "reason": "Model training was not run for this problem type."}

            if problem_info["problem_type"] in ("classification", "regression") and analysis.target_column:
                # 7. Model selection
                self._set_stage(analysis, "model_selection")
                selector = ModelSelectionAgent()
                candidates = selector.run(problem_info["problem_type"], len(cleaned_df), len(ml_numeric_cols) + len(ml_categorical_cols))
                self.db.commit()

                # 8. Training + evaluation
                self._set_stage(analysis, "training")
                trainer = TrainingAgent()
                ml_results = trainer.run(
                    cleaned_df, analysis.target_column, problem_info["problem_type"],
                    candidates, ml_numeric_cols, ml_categorical_cols, analysis.id,
                )
                ml_results["excluded_columns"] = excluded_cols
                explain_sample = ml_results.pop("_explain_sample", None)
                analysis.ml_results_json = to_json_safe(ml_results)
                self.db.commit()

                for exp in ml_results["experiments"]:
                    self.db.add(ModelExperiment(
                        analysis_id=analysis.id,
                        model_name=exp["model_name"],
                        metrics_json=to_json_safe(exp.get("metrics")),
                        is_best=exp.get("is_best", False),
                        model_path=exp.get("model_path"),
                    ))
                self.db.commit()

                # 9. Explainability
                self._set_stage(analysis, "explainability")
                if ml_results.get("best_model_path"):
                    import joblib
                    bundle = joblib.load(ml_results["best_model_path"])
                    explain_agent = ExplainabilityAgent()
                    explainability = explain_agent.run(
                        bundle["pipeline"], ml_results["feature_columns"], X_sample=explain_sample
                    )
                analysis.explainability_json = to_json_safe(explainability)
                self.db.commit()
            elif problem_info["problem_type"] == "clustering":
                # 7-8. Unsupervised: real KMeans, k chosen by silhouette score
                self._set_stage(analysis, "training")
                clustering = ClusteringAgent().run(cleaned_df, ml_numeric_cols, ml_categorical_cols, analysis.id)
                ml_results = {
                    "problem_type": "clustering",
                    "note": problem_info.get("reason"),
                    "clustering": clustering,
                    "excluded_columns": excluded_cols,
                    "experiments": [],
                    "best_model_name": f"KMeans(k={clustering['best_k']})" if clustering.get("available") else None,
                }
                analysis.ml_results_json = to_json_safe(ml_results)
                if clustering.get("available"):
                    self.db.add(ModelExperiment(
                        analysis_id=analysis.id, model_name=ml_results["best_model_name"],
                        metrics_json=to_json_safe({"silhouette": clustering["silhouette"], "k": clustering["best_k"]}),
                        is_best=True, model_path=clustering.get("model_path"),
                    ))
                self._set_stage(analysis, "explainability")
                explainability = {
                    "available": False,
                    "reason": "Feature importance does not apply to unsupervised clustering. "
                              "See the cluster profiles and distinguishing features instead.",
                }
                analysis.explainability_json = to_json_safe(explainability)
                self.db.commit()
            else:
                analysis.ml_results_json = to_json_safe({"problem_type": problem_info["problem_type"], "note": problem_info.get("reason")})
                analysis.explainability_json = to_json_safe(explainability)
                self.db.commit()

            # 10. Insight generation
            self._set_stage(analysis, "insight_generation")
            insight_agent = InsightAgent()
            insights = insight_agent.run(
                profiling, quality.get("findings", []), eda_results.get("findings", []),
                ml_results, explainability,
            )
            analysis.insights_json = to_json_safe(insights)
            self.db.commit()

            # 11. Report generation
            self._set_stage(analysis, "report_generation")
            report_agent = ReportAgent()
            report = report_agent.run(
                analysis.id, dataset.original_filename, profiling, quality,
                cleaning_summary, eda_results, ml_results, explainability, insights,
            )
            self.db.add(Report(analysis_id=analysis.id, content_json=to_json_safe(report["sections"]), file_path=report["file_path"]))
            self.db.commit()

            self._set_stage(analysis, "completed", status="completed")
            analysis.completed_at = datetime.now(timezone.utc)
            dataset.status = "analyzed"
            self.db.commit()

        except Exception as e:
            logger.exception("Pipeline failed for analysis %s", analysis_id)
            analysis.status = "failed"
            analysis.error_message = str(e)
            self.db.commit()

    @staticmethod
    def _derive_quality_findings(profiling: dict) -> dict:
        findings = []
        total_missing = sum(profiling["missing_values"].values())
        if total_missing > 0:
            findings.append(f"{total_missing} missing value(s) detected across the dataset.")
        if profiling["duplicate_rows"] > 0:
            findings.append(f"{profiling['duplicate_rows']} duplicate row(s) detected.")
        if profiling["constant_columns"]:
            findings.append(f"Constant column(s) with no variance: {profiling['constant_columns']}.")
        if profiling["duplicate_columns"]:
            findings.append(f"Duplicate column group(s) detected: {profiling['duplicate_columns']}.")
        if profiling["high_cardinality_columns"]:
            findings.append(f"High-cardinality column(s): {profiling['high_cardinality_columns']}.")
        if not findings:
            findings.append("No major data-quality issues were detected.")

        quality_score = 100
        quality_score -= min(40, total_missing)
        quality_score -= min(20, profiling["duplicate_rows"])
        quality_score -= 10 * len(profiling["constant_columns"])
        quality_score -= 10 * len(profiling["duplicate_columns"])
        quality_score = max(0, min(100, quality_score))

        return {
            "quality_score": quality_score,
            "findings": findings,
            "missing_values": profiling["missing_values"],
            "duplicate_rows": profiling["duplicate_rows"],
            "constant_columns": profiling["constant_columns"],
            "duplicate_columns": profiling["duplicate_columns"],
            "high_cardinality_columns": profiling["high_cardinality_columns"],
        }
