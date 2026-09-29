from pydantic import BaseModel
from datetime import datetime
from typing import Any


class ReportOut(BaseModel):
    id: int
    analysis_id: int
    content: Any
    file_path: str | None
    generated_at: datetime

    class Config:
        from_attributes = True
