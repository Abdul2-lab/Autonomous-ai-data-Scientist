from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False, unique=True)
    stored_path = Column(String, nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    file_extension = Column(String, nullable=False)
    rows = Column(Integer, nullable=True)
    columns = Column(Integer, nullable=True)
    status = Column(String, default="uploaded")  # uploaded/profiled/cleaned/analyzed/failed
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
