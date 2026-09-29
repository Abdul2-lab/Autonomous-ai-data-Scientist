"""
Custom exceptions + FastAPI exception handlers.
No raw stack traces are ever returned to the client.
"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("app")


class AppError(Exception):
    """Base application error with a user-friendly message."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class FileValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class DatasetNotFoundError(AppError):
    def __init__(self, dataset_id: int):
        super().__init__(f"Dataset {dataset_id} was not found.", status.HTTP_404_NOT_FOUND)


class AnalysisNotFoundError(AppError):
    def __init__(self, analysis_id: int):
        super().__init__(f"Analysis {analysis_id} was not found.", status.HTTP_404_NOT_FOUND)


class AnalysisStageError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class LLMNotConfiguredError(AppError):
    def __init__(self):
        super().__init__(
            "AI features require an LLM API key. Set OPENAI_API_KEY in your .env file "
            "to enable AI-generated explanations and chat. Core data analysis works without it.",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )


async def app_error_handler(request: Request, exc: AppError):
    logger.warning("AppError on %s: %s", request.url.path, exc.message)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again or check server logs."},
    )
