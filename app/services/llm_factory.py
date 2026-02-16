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
    "google_genai": "google",
    "google_vertexai": "google",
    "gemini": "google",
    "anthropic": "anthropic",
    "claude": "anthropic",
}


def _parse_model_name(raw: str) -> tuple[str, str]:
    """
    Parse 'provider:model' string.
    Returns (provider, model_name). Defaults to 'openai' if no prefix.
    """
    if ":" in raw:
        provider_raw, model_name = raw.split(":", 1)
        provider = _PROVIDER_ALIASES.get(provider_raw.lower(), provider_raw.lower())
        return provider, model_name
    return "openai", raw


def create_llm(
    model_name: str,
    api_key: str,
    temperature: float = 0.0,
) -> BaseChatModel:
    """
    Create a LangChain chat model based on the provider prefix.

    Args:
        model_name: Model identifier, optionally prefixed with provider
                    (e.g. "openai:gpt-4o-mini", "google:gemini-2.5-flash",
                    "anthropic:claude-sonnet-4-20250514").
        api_key: API key for the chosen provider.
        temperature: Sampling temperature.

    Returns:
        A LangChain BaseChatModel instance.

    Raises:
        ValueError: If the provider is not supported.
    """
    provider, model = _parse_model_name(model_name)

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
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
        )

    else:
        supported = sorted(set(_PROVIDER_ALIASES.values()))
        raise ValueError(
            f"Unsupported LLM provider '{provider}'. "
            f"Supported providers: {supported}. "
            f"Use format 'provider:model_name' in LLM_MODEL_NAME."
        )
