from fastapi import APIRouter, UploadFile, File, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetOut, DatasetPreview
from app.core.file_validation import save_upload
from app.core.exceptions import DatasetNotFoundError
from app.utils.helpers import load_dataframe

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post("/upload", response_model=DatasetOut, status_code=status.HTTP_201_CREATED)
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    meta = await save_upload(file)
    df = load_dataframe(meta["stored_path"], meta["file_extension"])

    dataset = Dataset(
        original_filename=meta["original_filename"],
        stored_filename=meta["stored_filename"],
        stored_path=meta["stored_path"],
        file_size_bytes=meta["file_size_bytes"],
        file_extension=meta["file_extension"],
        rows=df.shape[0],
        columns=df.shape[1],
        status="uploaded",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("", response_model=list[DatasetOut])
def list_datasets(db: Session = Depends(get_db)):
    return db.query(Dataset).order_by(Dataset.uploaded_at.desc()).all()


@router.get("/{dataset_id}", response_model=DatasetPreview)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise DatasetNotFoundError(dataset_id)

    df = load_dataframe(dataset.stored_path, dataset.file_extension)
    preview = df.head(20).astype(object).where(df.head(20).notnull(), None)

    return {
        "dataset": dataset,
        "columns": df.columns.tolist(),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "preview_rows": preview.to_dict(orient="records"),
    }
