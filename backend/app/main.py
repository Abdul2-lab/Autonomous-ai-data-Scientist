from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.core.logging_config import setup_logging
from app.core.exceptions import AppError, app_error_handler, unhandled_exception_handler

from app.api import datasets, analysis, chat, reports, health

setup_logging()

app = FastAPI(
    title="Autonomous AI Data Scientist API",
    description="Agentic AI-powered data analysis, ML, and insight generation platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(health.router)
app.include_router(datasets.router)
app.include_router(analysis.router)
app.include_router(chat.router)
app.include_router(reports.router)


@app.on_event("startup")
def on_startup():
    init_db()
