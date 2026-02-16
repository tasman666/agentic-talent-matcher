"""
LLM provider factory.
Supports OpenAI, Google (Gemini), and Anthropic (Claude) via LangChain.

Model names in .env use the format:  provider:model_name
Examples:
    LLM_MODEL_NAME=openai:gpt-4o-mini
    LLM_MODEL_NAME=google:gemini-2.5-flash
    LLM_MODEL_NAME=anthropic:claude-sonnet-4-20250514

If no provider prefix is given, defaults to OpenAI.
"""

from langchain_core.language_models.chat_models import BaseChatModel


_PROVIDER_ALIASES = {
    "openai": "openai",
    "google": "google",
    "gemini": "google",
    "anthropic": "anthropic",
    "claude": "anthropic",
    "ollama": "ollama",
    "local": "local",  # Generic OpenAI-compatible local server (LM Studio, vLLM)
}


def _parse_model_name(raw: str) -> tuple[str, str]:
    if ":" in raw:
        provider_raw, model_name = raw.split(":", 1)
        provider = _PROVIDER_ALIASES.get(provider_raw.lower(), provider_raw.lower())
        return provider, model_name
    return "openai", raw


def create_llm(
    model_name: str,
    api_key: str,
    base_url: str | None = None,
    temperature: float = 0.0,
) -> BaseChatModel:
    """
    Create a LangChain chat model based on the provider prefix.

    Args:
        model_name: "provider:model" string.
        api_key: API key.
        base_url: Optional base URL for local/custom endpoints.
        temperature: Sampling temperature.
    """
    provider, model = _parse_model_name(model_name)

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=base_url,
        )

    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=base_url,
        )

    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        # Default Ollama URL if not provided
        base_url = base_url or "http://localhost:11434"
        return ChatOllama(
            model=model,
            temperature=temperature,
            base_url=base_url,
        )

    elif provider == "local":
        # Use ChatOpenAI client but point to local server (e.g. LM Studio)
        from langchain_openai import ChatOpenAI
        base_url = base_url or "http://localhost:1234/v1"
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key or "lm-studio",
            base_url=base_url,
        )

    else:
        supported = sorted(set(_PROVIDER_ALIASES.values()))
        raise ValueError(f"Unsupported provider '{provider}'. Supported: {supported}")

