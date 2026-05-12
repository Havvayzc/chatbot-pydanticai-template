"""
Pipeline-Orchestrierung: Generator → Judge → Correct (Loop) → Auto-Layout.

Ablauf:
  1. Generator erzeugt BPMN aus Transkript
  2. Judge prüft semantisch (Coverage, Faithfulness, Reihenfolge, Akteure)
  3. Bei kritischen Findings: Generator korrigiert, zurück zu 2
  4. Bei keinen kritischen Findings: Auto-Layout anwenden
  5. Finales BPMN zurückgeben
"""

import logging

from .config import MAX_JUDGE_ITERATIONS
from .generator import correct_bpmn, generate_bpmn
from .judge import judge_bpmn

logger = logging.getLogger(__name__)


async def run_pipeline(transcript: str) -> str:
    """
    Führt die komplette BPMN-Pipeline aus.

    Returns:
        Valides, semantisch geprüftes, layoutetes BPMN-2.0-XML.
    """
    xml = await generate_bpmn(transcript)

    for iteration in range(1, MAX_JUDGE_ITERATIONS + 1):
        result = await judge_bpmn(transcript, xml)

        if not result.has_critical_findings():
            logger.info(f"Pipeline: Judge-Iteration {iteration} — keine kritischen Findings.")
            break

        critical = [f for f in result.findings if f.critical]
        logger.info(f"Pipeline: Iteration {iteration} — {len(critical)} kritische Findings, starte Korrektur.")

        xml = await correct_bpmn(transcript, xml, result.correction_instructions)
    else:
        logger.warning("Pipeline: Max. Judge-Iterationen erreicht — gebe letztes XML zurück.")

    return xml
