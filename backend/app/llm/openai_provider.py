"""
OpenAI-backed LLM provider. Reads the API key strictly from environment
configuration -- never hardcoded, never logged.
"""
from app.llm.base_provider import LLMProvider
from app.config import settings
from app.core.exceptions import LLMNotConfiguredError


class OpenAIProvider(LLMProvider):
    def __init__(self):
        if not settings.OPENAI_API_KEY.strip():
            raise LLMNotConfiguredError()
        # Imported lazily so the package is only required when actually used.
        from openai import OpenAI
        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        if settings.LLM_BASE_URL.strip():
            # Points the same OpenAI SDK at an OpenAI-compatible free-tier
            # provider (e.g. Groq: https://api.groq.com/openai/v1) instead
            # of OpenAI's own paid endpoint.
            client_kwargs["base_url"] = settings.LLM_BASE_URL.strip()
        self._client = OpenAI(**client_kwargs)
        self._model = settings.LLM_MODEL

    def generate(self, prompt: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.2,
            max_tokens=2000,
        )
        return response.choices[0].message.content or ""
