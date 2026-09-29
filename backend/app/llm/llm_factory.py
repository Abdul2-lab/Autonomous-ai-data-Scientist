from app.config import settings, llm_is_configured
from app.llm.openai_provider import OpenAIProvider
from app.llm.base_provider import LLMProvider


def get_llm_provider() -> LLMProvider | None:
    """Returns a usable LLM provider, or None if no key is configured.
    Core data-science features must never depend on this returning non-None."""
    if not llm_is_configured():
        return None
    if settings.LLM_PROVIDER == "openai":
        return OpenAIProvider()
    return None
