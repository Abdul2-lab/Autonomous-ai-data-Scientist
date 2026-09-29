import json
import os
from fastapi import APIRouter, Depends, BackgroundTasks, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models.dataset import Dataset
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate, AnalysisStatus, AnalysisResults
from app.config import settings
from app.core.exceptions import DatasetNotFoundError, AnalysisNotFoundError, AnalysisStageError
from app.utils.helpers import from_json_safe
from app.orchestrator.pipeline import AnalysisPipeline

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def _run_pipeline_background(analysis_id: int, target_column: str | None):
    """Runs in a background thread with its own DB session (per FastAPI BackgroundTasks pattern)."""
    db = SessionLocal()
    try:
        pipeline = AnalysisPipeline(db)
        pipeline.run_full_pipeline(analysis_id, target_column)
    finally:
        db.close()


def _public_cleaning(cleaning: dict | None) -> dict | None:
    """Hide internal server paths from API responses."""
    if not cleaning:
        return cleaning
    public = {k: v for k, v in cleaning.items() if k != "processed_file_path"}
    public["cleaned_dataset_available"] = bool(cleaning.get("processed_file_path"))
    return public


def _public_ml_results(ml: dict | None) -> dict | None:
    if not ml:
        return ml
    ml = dict(ml)
    ml.pop("best_model_path", None)
    ml["experiments"] = [{k: v for k, v in e.items() if k != "model_path"} for e in ml.get("experiments", [])]
    if isinstance(ml.get("clustering"), dict):
        ml["clustering"] = {k: v for k, v in ml["clustering"].items() if k != "model_path"}
    return ml


@router.post("", response_model=AnalysisStatus, status_code=status.HTTP_202_ACCEPTED)
def start_analysis(payload: AnalysisCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == payload.dataset_id).first()
    if not dataset:
        raise DatasetNotFoundError(payload.dataset_id)

    analysis = Analysis(dataset_id=dataset.id, status="pending", current_stage="queued",
                         target_column=payload.target_column)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    background_tasks.add_task(_run_pipeline_background, analysis.id, payload.target_column)
    return analysis


@router.get("/{analysis_id}/status", response_model=AnalysisStatus)
def get_status(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)
    return analysis


@router.get("/{analysis_id}/results", response_model=AnalysisResults)
def get_results(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)

    return {
        "id": analysis.id,
        "status": analysis.status,
        "current_stage": analysis.current_stage,
        "problem_type": analysis.problem_type,
        "target_column": analysis.target_column,
        "profiling": from_json_safe(analysis.profiling_json),
        "quality": from_json_safe(analysis.quality_json),
        "cleaning": _public_cleaning(from_json_safe(analysis.cleaning_json)),
        "eda": from_json_safe(analysis.eda_json),
        "visualizations": from_json_safe(analysis.visualization_json),
        "ml_results": _public_ml_results(from_json_safe(analysis.ml_results_json)),
        "explainability": from_json_safe(analysis.explainability_json),
        "insights": from_json_safe(analysis.insights_json),
        "error_message": analysis.error_message,
    }


@router.get("", response_model=list[AnalysisStatus])
def list_analyses(db: Session = Depends(get_db)):
    return db.query(Analysis).order_by(Analysis.created_at.desc()).all()


def _get_analysis_or_404(analysis_id: int, db: Session) -> Analysis:
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)
    return analysis


@router.get("/{analysis_id}/cleaned-dataset")
def download_cleaned_dataset(analysis_id: int, db: Session = Depends(get_db)):
    """Download the cleaned copy of the dataset produced by the Data Cleaning agent.
    The original upload is never modified; this is always a separate processed file."""
    analysis = _get_analysis_or_404(analysis_id, db)
    cleaning = from_json_safe(analysis.cleaning_json) or {}
    path = cleaning.get("processed_file_path")
    if not path:
        raise AnalysisStageError("The cleaned dataset is not available yet. Wait for the cleaning stage to finish.")

    # Path-traversal defence: only serve files that live inside the processed directory.
    processed_root = os.path.abspath(settings.PROCESSED_DIR)
    resolved = os.path.abspath(path)
    if not resolved.startswith(processed_root + os.sep) or not os.path.isfile(resolved):
        raise AnalysisStageError("The cleaned dataset file could not be found on the server.")

    dataset = db.query(Dataset).filter(Dataset.id == analysis.dataset_id).first()
    base = os.path.splitext(dataset.original_filename)[0] if dataset else f"analysis_{analysis_id}"
    return FileResponse(resolved, media_type="text/csv", filename=f"cleaned_{base}.csv")


@router.get("/{analysis_id}/export")
def export_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Download every computed result of an analysis as one JSON file."""
    analysis = _get_analysis_or_404(analysis_id, db)
    ml = from_json_safe(analysis.ml_results_json)
    if isinstance(ml, dict) and isinstance(ml.get("clustering"), dict):
        ml["clustering"].pop("model_path", None)
    payload = {
        "analysis_id": analysis.id,
        "dataset_id": analysis.dataset_id,
        "status": analysis.status,
        "problem_type": analysis.problem_type,
        "target_column": analysis.target_column,
        "profiling": from_json_safe(analysis.profiling_json),
        "quality": from_json_safe(analysis.quality_json),
        "cleaning": {k: v for k, v in (from_json_safe(analysis.cleaning_json) or {}).items()
                     if k != "processed_file_path"},
        "eda": from_json_safe(analysis.eda_json),
        "ml_results": ml,
        "explainability": from_json_safe(analysis.explainability_json),
        "insights": from_json_safe(analysis.insights_json),
    }
    return Response(
        content=json.dumps(payload, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="analysis_{analysis_id}_export.json"'},
    )
