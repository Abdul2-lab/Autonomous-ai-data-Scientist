from fastapi import APIRouter
from app.config import llm_is_configured

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "llm_configured": llm_is_configured(),
    }
