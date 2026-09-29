from sqlalchemy import Column, Integer, ForeignKey, Text, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)

    content_json = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())
