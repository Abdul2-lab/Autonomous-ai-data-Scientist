"""
AI Data Scientist chat endpoint. Answers are grounded strictly in the stored
analysis results via safe tool functions -- never via arbitrary code execution,
and never inventing numbers.
"""
import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import Analysis
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.exceptions import AnalysisNotFoundError
from app.utils.helpers import from_json_safe
from app.llm.llm_factory import get_llm_provider
from app.llm import tools as tool_fns

router = APIRouter(prefix="/api/analysis", tags=["chat"])

SYSTEM_PROMPT = (
    "You are an AI Data Scientist assistant. You will be given structured facts about a "
    "dataset and its analysis. Answer the user's question using ONLY those facts. "
    "If the facts don't contain enough information to answer confidently, respond exactly with: "
    "\"I don't have enough evidence from the current dataset to answer that confidently.\" "
    "Never invent numbers, columns, or results that are not in the provided facts."
)


def _build_context(analysis: Analysis) -> dict:
    return {
        "profiling": from_json_safe(analysis.profiling_json),
        "quality": from_json_safe(analysis.quality_json),
        "cleaning": from_json_safe(analysis.cleaning_json),
        "eda": from_json_safe(analysis.eda_json),
        "visualizations": from_json_safe(analysis.visualization_json),
        "ml_results": from_json_safe(analysis.ml_results_json),
        "explainability": from_json_safe(analysis.explainability_json),
        "insights": from_json_safe(analysis.insights_json),
    }


def _select_relevant_facts(context: dict, question: str) -> dict:
    """Keyword-routes the question to the safe tool(s) most likely to answer it."""
    q = question.lower()
    facts = {}

    if any(k in q for k in ["missing", "null", "nan"]):
        facts["missing_values"] = tool_fns.get_missing_values(context)
    if any(k in q for k in ["correlat", "relationship", "relate"]):
        facts["correlations"] = tool_fns.calculate_correlation(context)
    if any(k in q for k in ["important", "feature", "influen"]):
        facts["feature_importance"] = tool_fns.get_feature_importance(context)
    if any(k in q for k in ["model", "best", "accuracy", "performance", "f1", "score"]):
        facts["model_results"] = tool_fns.get_model_results(context)
    if any(k in q for k in ["pattern", "finding", "insight", "summary", "explain"]):
        facts["summary"] = tool_fns.get_analysis_summary(context)
    match = re.search(r"column[s]?\s+['\"]?([a-zA-Z0-9_ ]+)['\"]?", q)
    if match:
        col = match.group(1).strip()
        facts["column_statistics"] = tool_fns.get_column_statistics(context, col)

    # Always include the full analysis summary so the model has complete context,
    # not just the keyword-matched slice (which can miss what the question needs).
    facts["summary"] = tool_fns.get_analysis_summary(context)

    return facts


@router.post("/{analysis_id}/chat", response_model=ChatResponse)
def chat_with_analysis(analysis_id: int, payload: ChatRequest, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise AnalysisNotFoundError(analysis_id)

    if analysis.status != "completed":
        return ChatResponse(
            answer=f"This analysis is still '{analysis.status}' (stage: {analysis.current_stage}). "
                   "Please wait until it completes before asking questions.",
            grounded=True,
            used_llm=False,
        )

    context = _build_context(analysis)
    facts = _select_relevant_facts(context, payload.message)

    provider = None
    try:
        provider = get_llm_provider()
    except Exception:
        provider = None

    if provider is None:
        # Deterministic, still-grounded fallback without an LLM key.
        answer_lines = ["Based on the computed analysis (AI phrasing unavailable without an LLM API key):"]
        for key, value in facts.items():
            answer_lines.append(f"- {key}: {value}")
        return ChatResponse(answer="\n".join(answer_lines), grounded=True, used_llm=False, sources=list(facts.keys()))

    prompt = (
        f"User question: {payload.message}\n\n"
        f"Relevant computed facts (JSON): {facts}\n\n"
        "Answer the question using only these facts."
    )
    try:
        answer = provider.generate(prompt, system=SYSTEM_PROMPT)
        return ChatResponse(answer=answer, grounded=True, used_llm=True, sources=list(facts.keys()))
    except Exception as e:
        return ChatResponse(
            answer=f"The AI provider could not be reached ({e}). Here are the raw facts instead: {facts}",
            grounded=True, used_llm=False, sources=list(facts.keys()),
        )
