"""
Semantik-Judge — BPMN-Pipeline Schritt 2.

PydanticAI Agent (Gemini) prüft das generierte BPMN gegen das Transkript
in 4 Dimensionen: Coverage, Faithfulness, Reihenfolge, Akteure.
"""

import logging
from pathlib import Path
from typing import Literal

import logfire
from pydantic import BaseModel

logfire.configure()
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .config import JUDGE_MODEL, LITELLM_API_KEY, LITELLM_BASE_URL

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "judge.txt").read_text(encoding="utf-8")


class Finding(BaseModel):
    dimension: Literal["coverage", "faithfulness", "reihenfolge", "akteure"]
    critical: bool
    description: str
    evidence: str


class JudgeResult(BaseModel):
    findings: list[Finding]
    correction_instructions: str

    def has_critical_findings(self) -> bool:
        return any(f.critical for f in self.findings)


_provider = OpenAIProvider(
    base_url=f"{LITELLM_BASE_URL}/v1",
    api_key=LITELLM_API_KEY,
)
_model = OpenAIChatModel(JUDGE_MODEL, provider=_provider)

_agent = Agent(
    model=_model,
    system_prompt=_SYSTEM_PROMPT,
    output_type=JudgeResult,
)


async def judge_bpmn(transcript: str, xml: str) -> JudgeResult:
    """
    Prüft das BPMN-XML semantisch gegen das Transkript.

    Returns:
        JudgeResult mit Findings und ggf. Korrekturanweisungen.
    """
    user_message = (
        f"Transkript:\n\n{transcript}\n\n"
        f"BPMN-XML:\n\n{xml}"
    )

    logger.info(f"Judge: Semantik-Prüfung mit {JUDGE_MODEL}...")
    result = await _agent.run(user_message)
    judge_result: JudgeResult = result.output

    critical_count = sum(1 for f in judge_result.findings if f.critical)
    logger.info(
        f"Judge: {len(judge_result.findings)} Findings "
        f"({critical_count} kritisch)."
    )

    logfire.info(
        "judge_result",
        findings=len(judge_result.findings),
        critical=critical_count,
    )

    return judge_result
