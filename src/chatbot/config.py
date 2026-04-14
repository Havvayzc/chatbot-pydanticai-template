"""
Extension point: System prompt and model selection.

Change DEFAULT_SYSTEM_PROMPT and DEFAULT_MODEL here to adapt the chatbot's
personality and which LLM provider/model it uses. You can also load these
from environment variables or a config file for different environments.

Backend mode (flag):
- Use OpenAI directly when OPENAI_API_KEY is set and USE_LITELLM is not set.
- Use LiteLLM when USE_LITELLM=1 (or when LITELLM_API_KEY and LITELLM_SERVER_URL are set).
  LiteLLM requires a running LiteLLM server (or proxy) and the corresponding API key.
"""

import os

# Default instructions sent to the model as the "system" role. This shapes
# how the assistant responds (tone, scope, rules).
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant. "
    "Answer concisely and clearly. If you don't know something, say so."
)

# Model identifier for OpenAI (or for LiteLLM, the model name passed to the proxy).
# Examples: "gpt-4o-mini", "openai/gpt-4o-mini" (LiteLLM format when using a proxy).
DEFAULT_MODEL = "openai:gpt-4o-mini"

# --- Backend selection: OpenAI direct vs LiteLLM ---
# Set USE_LITELLM=1 (or true/yes) to send requests to a LiteLLM server instead of OpenAI.
# When using LiteLLM, you must set LITELLM_SERVER_URL and LITELLM_API_KEY.
USE_LITELLM_ENV = os.environ.get("USE_LITELLM", "").strip().lower() in ("1", "true", "yes")
LITELLM_SERVER_URL_ENV = os.environ.get("LITELLM_SERVER_URL", "").strip() or None
LITELLM_API_KEY_ENV = os.environ.get("LITELLM_API_KEY", "").strip() or None

# Use LiteLLM if the flag is set or if both LiteLLM URL and key are present.
def use_litellm() -> bool:
    if USE_LITELLM_ENV:
        return True
    return bool(LITELLM_SERVER_URL_ENV and LITELLM_API_KEY_ENV)

# LiteLLM server URL (e.g. http://localhost:4000 or http://localhost:4000/v1 if the proxy exposes the API under /v1).
# The LiteLLM server must be running and configured to proxy to your desired providers.
LITELLM_SERVER_URL = LITELLM_SERVER_URL_ENV or "http://localhost:4000"

# API key for the LiteLLM server. Some setups use a placeholder; others require a key.
LITELLM_API_KEY = LITELLM_API_KEY_ENV or ""

# Model name sent to LiteLLM (e.g. "openai/gpt-4o-mini" to use OpenAI via LiteLLM).
LITELLM_MODEL = os.environ.get("LITELLM_MODEL", "").strip() or "gpt-4o-mini"
