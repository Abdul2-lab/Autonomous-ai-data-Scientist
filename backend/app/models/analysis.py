from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)

    status = Column(String, default="pending")  # pending/running/completed/failed
    current_stage = Column(String, default="not_started")
    problem_type = Column(String, nullable=True)
    target_column = Column(String, nullable=True)

    profiling_json = Column(Text, nullable=True)
    quality_json = Column(Text, nullable=True)
    cleaning_json = Column(Text, nullable=True)
    eda_json = Column(Text, nullable=True)
    visualization_json = Column(Text, nullable=True)
    ml_results_json = Column(Text, nullable=True)
    explainability_json = Column(Text, nullable=True)
    insights_json = Column(Text, nullable=True)

    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
