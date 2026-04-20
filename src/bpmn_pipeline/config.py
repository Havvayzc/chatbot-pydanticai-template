"""
Pipeline configuration — loaded from environment variables / .env file.

Model selection:
- If LITELLM_SERVER_URL is set → use HKA LiteLLM proxy for all models
- Otherwise → use provider SDKs directly (needs ANTHROPIC_API_KEY / GEMINI_API_KEY)
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai.models import Model

load_dotenv()

# --- LiteLLM Proxy (HKA) ---
LITELLM_SERVER_URL: str = os.environ.get("LITELLM_SERVER_URL", "").strip()
LITELLM_API_KEY: str = os.environ.get("LITELLM_API_KEY", "").strip()

# --- Fallback: direct API keys ---
ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "").strip()
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "").strip()

# --- Model names ---
GENERATOR_MODEL_NAME: str = os.environ.get("GENERATOR_MODEL", "claude-opus-4-6")
JUDGE_MODEL_NAME: str = os.environ.get("JUDGE_MODEL", "gemini-2.5-pro")

# --- Pipeline settings ---
MAX_ITERATIONS: int = int(os.environ.get("MAX_ITERATIONS", "3"))

# --- Paths ---
NODE_DIR: Path = Path(__file__).parent.parent.parent / "node"


def _use_litellm() -> bool:
    return bool(LITELLM_SERVER_URL and LITELLM_API_KEY)


def build_model(model_name: str) -> Model | str:
    """
    Return a pydantic-ai model instance.

    - With LiteLLM proxy (HKA): returns OpenAIChatModel pointing at the proxy.
    - Without proxy: returns the model name string (pydantic-ai resolves the provider
      from the prefix, e.g. 'anthropic:claude-opus-4-6').
    """
    if _use_litellm():
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai.providers.litellm import LiteLLMProvider

        provider = LiteLLMProvider(
            api_base=LITELLM_SERVER_URL,
            api_key=LITELLM_API_KEY,
        )
        return OpenAIChatModel(model_name, provider=provider)

    # Direct provider — model_name must include prefix, e.g. 'anthropic:claude-opus-4-6'
    return model_name
