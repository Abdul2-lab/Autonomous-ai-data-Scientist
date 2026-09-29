"""
Application configuration.
All values are loaded from environment variables (.env file), never hardcoded.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = f"sqlite:///{(BASE_DIR / 'data' / 'app.db').as_posix()}"

    # LLM configuration -- optional. App must work without these.
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "openai/gpt-oss-20b"
    LLM_PROVIDER: str = "openai"
    # Leave blank to use OpenAI's own endpoint. Set to an OpenAI-compatible
    # endpoint (e.g. https://api.groq.com/openai/v1) to use a free-tier
    # provider like Groq with the same OPENAI_API_KEY field and SDK.
    LLM_BASE_URL: str = ""

    # Upload limits / safety
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: tuple = (".csv", ".xlsx", ".xls")

    UPLOAD_DIR: str = str(BASE_DIR / "data" / "uploads")
    PROCESSED_DIR: str = str(BASE_DIR / "data" / "processed")
    MODELS_DIR: str = str(BASE_DIR / "models_store")
    REPORTS_DIR: str = str(BASE_DIR / "reports_store")
    LOG_DIR: str = str(BASE_DIR / "logs")

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    class Config:
        env_file = str(BASE_DIR / ".env")
        case_sensitive = True


settings = Settings()

# Ensure required directories exist at import time.
for _dir in (
    settings.UPLOAD_DIR,
    settings.PROCESSED_DIR,
    settings.MODELS_DIR,
    settings.REPORTS_DIR,
    settings.LOG_DIR,
    str(Path(settings.DATABASE_URL.replace("sqlite:///", "")).parent),
):
    os.makedirs(_dir, exist_ok=True)


def llm_is_configured() -> bool:
    """Whether an LLM provider is usable. Core data-science features never depend on this."""
    return bool(settings.OPENAI_API_KEY.strip())
