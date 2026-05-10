"""Runtime configuration helpers for local and cloud deployments."""

import os


def get_runtime_value(name: str, default=None):
    """
    Read a runtime value from Streamlit secrets or environment variables.

    Streamlit Cloud stores secrets in st.secrets. Local development can use
    normal environment variables. This helper is intentionally safe to import
    outside Streamlit, for tests and scripts.
    """

    try:
        import streamlit as st

        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass

    return os.environ.get(name, default)


def get_ai_provider(config: dict) -> str:
    """Return the active AI provider, allowing cloud secrets to override config."""

    provider = get_runtime_value("AI_PROVIDER")
    if not provider:
        provider = config.get("model", {}).get("provider", "ollama")

    return str(provider).strip().lower()


def get_openai_api_key() -> str | None:
    """Return the OpenAI API key from Streamlit secrets or environment variables."""

    key = get_runtime_value("OPENAI_API_KEY")
    if key:
        return str(key)

    return None


def require_openai_api_key() -> str:
    """Return the OpenAI API key or raise a deployment-friendly error."""

    key = get_openai_api_key()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is required when provider is set to openai. "
            "Add it to Streamlit Cloud secrets or set it as an environment variable."
        )

    return key
