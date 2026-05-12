"""
Configuration — lädt .env und baut den LLM-Client.

Der HKA-Proxy unterstützt den nativen Anthropic-Beta-Endpunkt nicht.
Daher: OpenAI-kompatibler LiteLLM-Endpunkt (funktioniert mit claude-opus-4-6 und gemini).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

LITELLM_BASE_URL: str = os.environ["LITELLM_BASE_URL"]
LITELLM_API_KEY: str = os.environ["LITELLM_API_KEY"]
ANTHROPIC_BASE_URL: str = os.environ["ANTHROPIC_BASE_URL"]
ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
GEMINI_BASE_URL: str = os.environ["GEMINI_BASE_URL"]
GEMINI_API_KEY: str = os.environ["GEMINI_API_KEY"]
GENERATOR_MODEL: str = os.getenv("GENERATOR_MODEL", "claude-opus-4-6")
JUDGE_MODEL: str = os.getenv("JUDGE_MODEL", "gemini-2.5-pro")
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "32768"))
MAX_JUDGE_ITERATIONS: int = int(os.getenv("MAX_JUDGE_ITERATIONS", "2"))
