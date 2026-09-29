from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DatasetOut(BaseModel):
    id: int
    original_filename: str
    file_size_bytes: int
    file_extension: str
    rows: Optional[int] = None
    columns: Optional[int] = None
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DatasetPreview(BaseModel):
    dataset: DatasetOut
    columns: list[str]
    dtypes: dict[str, str]
    preview_rows: list[dict]
