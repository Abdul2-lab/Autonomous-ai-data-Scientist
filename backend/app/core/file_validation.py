"""
Upload safety: extension whitelist, size limit, filename sanitization,
path-traversal prevention, unique storage naming.
"""
import os
import re
import uuid
from fastapi import UploadFile

from app.config import settings
from app.core.exceptions import FileValidationError

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_.-]")


def sanitize_filename(filename: str) -> str:
    """Strip directory components and unsafe characters to prevent path traversal."""
    base = os.path.basename(filename)
    base = base.replace("..", "")
    base = _SAFE_NAME_RE.sub("_", base)
    if not base:
        base = "upload"
    return base


def validate_extension(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file type '{ext}'. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    return ext


def validate_size(size_bytes: int):
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise FileValidationError(
            f"File is too large ({size_bytes / (1024*1024):.1f} MB). "
            f"Maximum allowed size is {settings.MAX_UPLOAD_SIZE_MB} MB."
        )
    if size_bytes == 0:
        raise FileValidationError("The uploaded file is empty.")


def generate_stored_path(original_filename: str, ext: str) -> tuple[str, str]:
    """Returns (stored_filename, absolute_stored_path) inside the upload dir only."""
    stored_filename = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_filename)
    # Defense in depth: ensure the resolved path is still inside UPLOAD_DIR.
    resolved = os.path.abspath(stored_path)
    if not resolved.startswith(os.path.abspath(settings.UPLOAD_DIR)):
        raise FileValidationError("Invalid upload path.")
    return stored_filename, stored_path


async def save_upload(file: UploadFile) -> dict:
    """Validates and persists an uploaded file. Returns metadata dict."""
    original_name = sanitize_filename(file.filename or "upload")
    ext = validate_extension(original_name)

    contents = await file.read()
    validate_size(len(contents))

    stored_filename, stored_path = generate_stored_path(original_name, ext)
    with open(stored_path, "wb") as f:
        f.write(contents)

    return {
        "original_filename": original_name,
        "stored_filename": stored_filename,
        "stored_path": stored_path,
        "file_size_bytes": len(contents),
        "file_extension": ext,
    }
