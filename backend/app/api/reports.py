from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import Analysis
from app.models.report import Report
from app.core.exceptions import AnalysisNotFoundError, AnalysisStageError
from app.utils.helpers import from_json_safe

router = APIRouter(prefix="/api/analysis", tags=["reports"])


@router.post("/{analysis_id}/report")
def get_or_confirm_report(analysis_id: int, db: Session = Depends(get_db)):
    """Reports are generated automatically as the final pipeline stage.
    This endpoint returns the existing report, or a clear message if it isn't ready yet."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)

    report = db.query(Report).filter(Report.analysis_id == analysis_id).order_by(Report.generated_at.desc()).first()
    if not report:
        raise AnalysisStageError(
            f"Report not yet available. Current stage: '{analysis.current_stage}' (status: '{analysis.status}')."
        )
    return {"id": report.id, "analysis_id": report.analysis_id, "content": from_json_safe(report.content_json),
            "file_path": report.file_path, "generated_at": report.generated_at}


@router.get("/{analysis_id}/report")
def download_report(analysis_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.analysis_id == analysis_id).order_by(Report.generated_at.desc()).first()
    if not report:
        raise AnalysisStageError("Report not yet available for this analysis.")
    return FileResponse(report.file_path, media_type="text/html", filename=f"report_{analysis_id}.html")
