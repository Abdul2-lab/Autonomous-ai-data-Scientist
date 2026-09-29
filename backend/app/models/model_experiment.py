from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ModelExperiment(Base):
    __tablename__ = "model_experiments"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)

    model_name = Column(String, nullable=False)
    params_json = Column(Text, nullable=True)
    metrics_json = Column(Text, nullable=True)
    is_best = Column(Boolean, default=False)
    model_path = Column(String, nullable=True)

    trained_at = Column(DateTime(timezone=True), server_default=func.now())
