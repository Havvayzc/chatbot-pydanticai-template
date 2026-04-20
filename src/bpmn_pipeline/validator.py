"""
Validator stage — calls Node.js scripts for schema parsing and soundness checks.

validate_bpmn():  bpmn-moddle (schema) + bpmnlint (soundness)
apply_layout():   bpmn-auto-layout (adds DI coordinates)
"""

import asyncio
import json
import logging
import subprocess

from .config import NODE_DIR
from .models import ValidationResult

logger = logging.getLogger(__name__)


async def validate_bpmn(xml: str) -> ValidationResult:
    """
    Run bpmn-moddle schema parsing and bpmnlint soundness check via Node.js.

    Returns a ValidationResult with any errors found.
    """
    script = NODE_DIR / "validate.js"
    if not script.exists():
        raise RuntimeError(
            f"Node.js validation script not found at {script}. "
            "Run 'npm install' inside the node/ directory first."
        )

    stdout, stderr, returncode = await _run_node(str(script), xml)

    if returncode != 0:
        error_msg = stderr or "Unknown Node.js error"
        logger.error(f"validate.js exited with code {returncode}: {error_msg}")
        return ValidationResult(success=False, moddle_errors=[f"Node.js error: {error_msg}"])

    try:
        data = json.loads(stdout)
        return ValidationResult(**data)
    except Exception as exc:
        logger.error(f"Could not parse validate.js output: {exc}\nRaw output: {stdout[:500]}")
        return ValidationResult(success=False, moddle_errors=[f"Could not parse validation result: {exc}"])


async def apply_layout(xml: str) -> str:
    """
    Apply deterministic auto-layout to the BPMN XML via bpmn-auto-layout (Node.js).

    Returns the XML with BPMNDI coordinates added.
    Falls back to the original XML if layout fails (non-fatal).
    """
    script = NODE_DIR / "layout.js"
    if not script.exists():
        logger.warning(f"layout.js not found at {script} — returning XML without layout.")
        return xml

    stdout, stderr, returncode = await _run_node(str(script), xml)

    if returncode != 0:
        logger.warning(f"layout.js failed (code {returncode}): {stderr} — returning XML without layout.")
        return xml

    return stdout


async def _run_node(script_path: str, stdin_data: str) -> tuple[str, str, int]:
    """
    Run a Node.js script in a thread pool executor.

    asyncio.create_subprocess_exec does NOT work reliably on Windows inside
    uvicorn's event loop (raises NotImplementedError with SelectorEventLoop).
    Using asyncio.to_thread + subprocess.run works on all platforms.
    """
    def _sync() -> tuple[str, str, int]:
        proc = subprocess.run(
            ["node", script_path],
            input=stdin_data.encode("utf-8"),
            capture_output=True,
            timeout=60,
        )
        return (
            proc.stdout.decode("utf-8", errors="replace"),
            proc.stderr.decode("utf-8", errors="replace"),
            proc.returncode,
        )

    return await asyncio.to_thread(_sync)
