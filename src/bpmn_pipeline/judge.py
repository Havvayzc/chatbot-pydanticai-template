"""
Semantik-Judge stage — evaluates the BPMN model against the transcript.

Four sub-checks:
  1. Coverage    — all transcript steps present in the model?
  2. Faithfulness — no hallucinated elements?
  3. Reihenfolge — correct sequence and gateway conditions?
  4. Akteure     — correct Pool/Lane assignment?

Each finding MUST contain a verbatim transcript quote as evidence.
Findings without evidence are filtered out (anti-hallucination measure).

Uses the OpenAI-compatible client directly (LiteLLM proxy is OpenAI-compatible).
The model name in config (JUDGE_MODEL_NAME) determines which AI is used — e.g. gemini-2.5-pro.
"""

import json
import logging
import re

from openai import AsyncOpenAI
from pydantic import ValidationError

from .config import JUDGE_MODEL_NAME, LITELLM_API_KEY, LITELLM_SERVER_URL
from .models import Finding, JudgeResult
from .prompts import JUDGE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(
    base_url=LITELLM_SERVER_URL,
    api_key=LITELLM_API_KEY,
)


async def judge_bpmn(transcript: str, bpmn_xml: str) -> JudgeResult:
    """
    Evaluate the BPMN model against the transcript.

    Returns a JudgeResult with findings (filtered to those with evidence).
    """
    user_message = (
        f"Transcript:\n\n{transcript}\n\n"
        f"---\n\n"
        f"BPMN XML to evaluate:\n\n{bpmn_xml}"
    )

    response = await _client.chat.completions.create(
        model=JUDGE_MODEL_NAME,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=4096,
        temperature=0.1,
    )

    raw = response.choices[0].message.content or ""
    return _parse_judge_output(raw)


def _parse_judge_output(raw: str) -> JudgeResult:
    """Parse the JSON response from the judge, with fallback on errors."""
    text = raw.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    # Extract JSON object if surrounded by extra text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    try:
        data = json.loads(text)
        raw_findings: list = data.get("findings", [])
        summary: str = data.get("summary", "No summary provided.")

        valid_findings: list[Finding] = []
        for f in raw_findings:
            try:
                finding = Finding(**f)
                if finding.evidence and finding.evidence.strip():
                    valid_findings.append(finding)
                else:
                    logger.warning(f"Judge: dropped finding without evidence: {f.get('description', '?')}")
            except (ValidationError, TypeError) as exc:
                logger.warning(f"Judge: skipped malformed finding: {exc}")

        return JudgeResult(findings=valid_findings, summary=summary)

    except (json.JSONDecodeError, KeyError) as exc:
        logger.error(f"Judge: could not parse response as JSON: {exc}\nRaw:\n{raw[:500]}")
        return JudgeResult(findings=[], summary=f"Judge parse error: {exc}")
