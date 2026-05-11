"""
BPMN Validator — PydanticAI Tool.

Ruft node/validate.js auf (bpmn-moddle + bpmnlint) und gibt einen
lesbaren Fehlerbericht zurück, den der Agent zum Korrigieren nutzen kann.
"""

import asyncio
import json
import subprocess
from pathlib import Path

from pydantic_ai import RunContext

_VALIDATE_JS = Path(__file__).parent.parent.parent / "node" / "validate.js"


async def validate_bpmn_tool(ctx: RunContext[None], xml: str) -> str:
    """
    Validiert BPMN-2.0-XML mit bpmn-moddle und bpmnlint.

    Gibt 'VALID' zurück wenn das XML fehlerfrei ist,
    sonst einen Fehlerbericht den du zum Korrigieren verwenden sollst.
    """
    def _run() -> tuple[str, int]:
        proc = subprocess.run(
            ["node", str(_VALIDATE_JS)],
            input=xml.encode("utf-8"),
            capture_output=True,
            timeout=60,
            cwd=str(_VALIDATE_JS.parent),
        )
        return proc.stdout.decode("utf-8", errors="replace"), proc.returncode

    try:
        stdout, _ = await asyncio.to_thread(_run)
        data = json.loads(stdout)
    except Exception as exc:
        return f"VALIDATOR ERROR: {exc}"

    if data.get("valid"):
        return "VALID"

    errors = data.get("errors", [])
    lines = [f"VALIDATION FAILED — {len(errors)} Fehler gefunden:\n"]
    for i, err in enumerate(errors, 1):
        rule = err.get("rule", "?")
        msg = err.get("message", "?")
        elem = err.get("id")
        line = f"  {i}. [{rule}] {msg}"
        if elem:
            line += f" (Element: {elem})"
        lines.append(line)

    lines.append("\nBitte behebe ALLE Fehler und erzeuge ein vollständig korrigiertes BPMN-2.0-XML.")
    return "\n".join(lines)
