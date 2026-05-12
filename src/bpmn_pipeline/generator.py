"""
Generator — BPMN-Pipeline Schritt 1.

PydanticAI Agent mit validate_bpmn_tool:
  1. Agent generiert BPMN-XML
  2. Ruft validate_bpmn_tool selbst auf
  3. Bei Fehlern: korrigiert und validiert erneut
  4. Gibt valides XML zurück
"""

import logging
import re
from pathlib import Path

import anthropic
import logfire
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

from .config import ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL, GENERATOR_MODEL, MAX_TOKENS
from .validator import validate_bpmn_tool

logfire.configure()
logfire.instrument_pydantic_ai()

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "generator.txt").read_text(encoding="utf-8")

_provider = AnthropicProvider(
    anthropic_client=anthropic.AsyncAnthropic(
        base_url=ANTHROPIC_BASE_URL,
        api_key=ANTHROPIC_API_KEY,
    )
)
_model = AnthropicModel(GENERATOR_MODEL, provider=_provider)

_agent = Agent(
    model=_model,
    system_prompt=_SYSTEM_PROMPT,
    output_type=str,
    tools=[validate_bpmn_tool],
    model_settings={"max_tokens": MAX_TOKENS},
)


async def correct_bpmn(transcript: str, current_xml: str, correction_instructions: str) -> str:
    """
    Korrigiert ein bestehendes BPMN anhand von Judge-Findings.
    """
    user_message = (
        f"Transkript:\n\n{transcript}\n\n"
        f"Aktuelles BPMN (enthält Fehler):\n\n{current_xml}\n\n"
        f"Korrekturanweisungen:\n\n{correction_instructions}"
    )
    logger.info("Generator: Korrektur-Durchlauf...")
    result = await _agent.run(user_message)
    raw: str = result.output
    logger.info(f"Generator: Korrektur — {len(raw)} Zeichen empfangen.")
    return _clean_xml(raw)


async def generate_bpmn(transcript: str) -> str:
    """
    Erzeuge valides BPMN-2.0-XML aus einem Transkript.

    Der Agent validiert das XML selbst mit validate_bpmn_tool
    und korrigiert Fehler eigenständig.

    Returns:
        BPMN-2.0-XML-String ohne Kommentare und ohne Markdown.
    """
    user_message = f"Transcript:\n\n{transcript}"

    logger.info(f"Generator: Anfrage an {GENERATOR_MODEL} ({MAX_TOKENS} max_tokens)...")
    result = await _agent.run(user_message)
    raw: str = result.output
    logger.info(f"Generator: {len(raw)} Zeichen empfangen.")
    return _clean_xml(raw)


def _clean_xml(text: str) -> str:
    """Entferne Markdown-Fences und alle XML-Kommentare."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    text = text.strip()
    match = re.search(r"<\?xml", text)
    if match:
        text = text[match.start():]
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
