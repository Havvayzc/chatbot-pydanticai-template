"""
Generator stage — Claude Opus 4.6 → BPMN 2.0 XML.

Uses the OpenAI-compatible client directly (LiteLLM proxy is OpenAI-compatible),
avoiding pydantic-ai's structured-output code paths that cause NotImplementedError.

On the first iteration the generator receives only the transcript.
On subsequent iterations it also receives the previous model's error report.
"""

import logging

from openai import AsyncOpenAI

from .config import GENERATOR_MODEL_NAME, LITELLM_API_KEY, LITELLM_SERVER_URL
from .prompts import GENERATOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(
    base_url=LITELLM_SERVER_URL,
    api_key=LITELLM_API_KEY,
)


async def generate_bpmn(transcript: str, feedback: str | None = None) -> str:
    """
    Generate BPMN 2.0 XML from a transcript.

    Args:
        transcript: The (censored) meeting transcript.
        feedback:   Error report from a previous iteration, or None on first run.

    Returns:
        BPMN 2.0 XML string (cleaned of any markdown wrapping).
    """
    if feedback is None:
        user_message = f"Transcript:\n\n{transcript}"
    else:
        user_message = (
            f"Transcript:\n\n{transcript}\n\n"
            f"---\n\n"
            f"Your previous BPMN model had the following issues. "
            f"Please fix ALL of them and generate a complete, corrected BPMN 2.0 XML:\n\n"
            f"{feedback}"
        )

    response = await _client.chat.completions.create(
        model=GENERATOR_MODEL_NAME,
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=16000,
        temperature=0.2,
    )

    raw = response.choices[0].message.content or ""
    logger.debug(f"Generator raw response length: {len(raw)}")
    return _clean_xml(raw)


def _clean_xml(text: str) -> str:
    """Strip markdown code fences that LLMs sometimes add despite instructions."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # remove opening ```xml or ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]  # remove closing ```
        text = "\n".join(lines)
    return text.strip()
