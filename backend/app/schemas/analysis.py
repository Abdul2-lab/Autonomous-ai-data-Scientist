from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class AnalysisCreate(BaseModel):
    dataset_id: int
    target_column: Optional[str] = None


class AnalysisStatus(BaseModel):
    id: int
    dataset_id: int
    status: str
    current_stage: str
    problem_type: Optional[str] = None
    target_column: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalysisResults(BaseModel):
    id: int
    status: str
    current_stage: str
    problem_type: Optional[str] = None
    target_column: Optional[str] = None
    profiling: Optional[Any] = None
    quality: Optional[Any] = None
    cleaning: Optional[Any] = None
    eda: Optional[Any] = None
    visualizations: Optional[Any] = None
    ml_results: Optional[Any] = None
    explainability: Optional[Any] = None
    insights: Optional[Any] = None
    error_message: Optional[str] = None
