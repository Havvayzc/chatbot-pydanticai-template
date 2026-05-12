"""
Auto-Layout — BPMN-Pipeline Schritt 3.

Ruft node/layout.js auf (bpmn-auto-layout) und gibt das layoutete XML zurück.
"""

import asyncio
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

_LAYOUT_JS = Path(__file__).parent.parent.parent / "node" / "layout.js"


async def apply_layout(xml: str) -> str:
    """
    Wendet bpmn-auto-layout auf das BPMN-XML an.

    Returns:
        BPMN-XML mit automatisch berechneten Koordinaten.
    """
    def _run() -> tuple[str, str, int]:
        proc = subprocess.run(
            ["node", str(_LAYOUT_JS)],
            input=xml.encode("utf-8"),
            capture_output=True,
            timeout=30,
            cwd=str(_LAYOUT_JS.parent),
        )
        return (
            proc.stdout.decode("utf-8", errors="replace"),
            proc.stderr.decode("utf-8", errors="replace"),
            proc.returncode,
        )

    stdout, stderr, returncode = await asyncio.to_thread(_run)

    if returncode != 0 or not stdout.strip():
        logger.warning(f"Auto-Layout fehlgeschlagen: {stderr} — gebe Original-XML zurück.")
        return xml

    logger.info("Auto-Layout erfolgreich angewendet.")
    return stdout
