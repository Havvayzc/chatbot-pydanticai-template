"""
Pipeline orchestration — runs all stages in the correct order with the iteration loop.

Flow per iteration:
  1. Generator  → BPMN XML
  2. Schema check (moddle) → errors? → back to Generator
  3. Soundness  (bpmnlint) → errors? → back to Generator
  4. Judge      (Gemini)   → critical findings? → back to Generator
  5. Auto-layout           → final BPMN XML

Max iterations: MAX_ITERATIONS (default 3). After that, return the last XML anyway.
"""

import logging

from .config import MAX_ITERATIONS
from .generator import generate_bpmn
from .judge import judge_bpmn
from .models import PipelineResult
from .validator import apply_layout, validate_bpmn

logger = logging.getLogger(__name__)


async def run_pipeline(transcript: str) -> PipelineResult:
    """
    Run the full transcript → BPMN pipeline.

    Args:
        transcript: The (censored) meeting transcript text.

    Returns:
        PipelineResult with the final BPMN XML and metadata.
    """
    feedback: str | None = None
    last_xml: str = ""
    judge_summary: str | None = None

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.info(f"--- Pipeline iteration {iteration}/{MAX_ITERATIONS} ---")

        # ── Stage 1: Generate ──────────────────────────────────────────────
        bpmn_xml = await generate_bpmn(transcript, feedback)
        last_xml = bpmn_xml
        logger.info(f"Generator produced {len(bpmn_xml)} chars of XML.")

        # ── Stage 2: Schema parsing (bpmn-moddle) ─────────────────────────
        validation = await validate_bpmn(bpmn_xml)

        if validation.moddle_errors:
            logger.warning(f"Schema errors (iter {iteration}): {validation.moddle_errors}")
            feedback = f"SCHEMA / PARSING ERRORS — fix the XML structure:\n{validation.to_error_report()}"
            continue

        # ── Stage 3: Model soundness (bpmnlint) ───────────────────────────
        if validation.lint_errors:
            logger.warning(f"Lint errors (iter {iteration}): {len(validation.lint_errors)} issue(s)")
            feedback = f"MODEL SOUNDNESS ERRORS — fix structural issues:\n{validation.to_error_report()}"
            continue

        logger.info("Validation passed (schema + soundness).")

        # ── Stage 4: Semantic judge ────────────────────────────────────────
        judge_result = await judge_bpmn(transcript, bpmn_xml)
        judge_summary = judge_result.summary
        logger.info(f"Judge summary: {judge_summary}")
        logger.info(
            f"Judge findings: {len(judge_result.critical_findings)} critical, "
            f"{len(judge_result.warning_findings)} warnings."
        )

        if judge_result.has_critical_findings:
            logger.warning(f"Critical findings (iter {iteration}) — sending back to generator.")
            findings_text = "\n".join(
                f"[{f.category.upper()}|{f.severity.upper()}] {f.description}\n"
                f'  Evidence: "{f.evidence}"'
                + (f"\n  Element: {f.element_id}" if f.element_id else "")
                for f in judge_result.critical_findings
            )
            feedback = f"SEMANTIC QUALITY ISSUES — correct the following:\n{findings_text}"
            continue

        # ── Stage 5: Auto-layout ──────────────────────────────────────────
        logger.info("Applying auto-layout...")
        final_xml = await apply_layout(bpmn_xml)

        # Safety check: validate the laid-out XML one more time
        final_check = await validate_bpmn(final_xml)
        if final_check.moddle_errors:
            logger.warning("Layout introduced XML errors — returning pre-layout XML.")
            final_xml = bpmn_xml

        warnings = [
            f"[{f.category}] {f.description}" for f in judge_result.warning_findings
        ]

        logger.info(f"Pipeline completed successfully in {iteration} iteration(s).")
        return PipelineResult(
            success=True,
            bpmn_xml=final_xml,
            iterations=iteration,
            warnings=warnings,
            judge_summary=judge_summary,
        )

    # ── Max iterations reached ────────────────────────────────────────────
    logger.warning(
        f"Max iterations ({MAX_ITERATIONS}) reached — returning last XML with layout applied."
    )
    final_xml = await apply_layout(last_xml)
    final_check = await validate_bpmn(final_xml)
    if final_check.moddle_errors:
        final_xml = last_xml  # fall back to pre-layout XML

    return PipelineResult(
        success=True,
        bpmn_xml=final_xml,
        iterations=MAX_ITERATIONS,
        warnings=["Maximum iterations reached — model may have residual issues."],
        max_iterations_reached=True,
        judge_summary=judge_summary,
    )
