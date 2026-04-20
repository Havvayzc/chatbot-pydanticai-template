"""
Pydantic models shared across the pipeline stages.
"""

from enum import Enum
from pydantic import BaseModel


class FindingSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"


class FindingCategory(str, Enum):
    COVERAGE = "coverage"
    FAITHFULNESS = "faithfulness"
    REIHENFOLGE = "reihenfolge"
    AKTEURE = "akteure"


class Finding(BaseModel):
    category: FindingCategory
    severity: FindingSeverity
    element_id: str | None = None
    description: str
    evidence: str  # Verbatim transcript quote — required, no evidence = no finding


class JudgeResult(BaseModel):
    findings: list[Finding]
    summary: str

    @property
    def has_critical_findings(self) -> bool:
        return any(f.severity == FindingSeverity.CRITICAL for f in self.findings)

    @property
    def critical_findings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == FindingSeverity.CRITICAL]

    @property
    def warning_findings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == FindingSeverity.WARNING]


class ValidationResult(BaseModel):
    success: bool
    moddle_errors: list[str] = []
    lint_errors: list[dict] = []

    @property
    def has_errors(self) -> bool:
        return bool(self.moddle_errors) or bool(self.lint_errors)

    def to_error_report(self) -> str:
        lines: list[str] = []
        if self.moddle_errors:
            lines.append("SCHEMA / PARSING ERRORS (fix the XML structure):")
            for e in self.moddle_errors:
                lines.append(f"  - {e}")
        if self.lint_errors:
            lines.append("MODEL SOUNDNESS ERRORS (bpmnlint:recommended violations):")
            for e in self.lint_errors:
                elem = f" (element: {e['id']})" if e.get("id") else ""
                lines.append(f"  - [{e.get('rule', '?')}] {e.get('message', str(e))}{elem}")
        return "\n".join(lines)


class PipelineResult(BaseModel):
    success: bool
    bpmn_xml: str
    iterations: int
    warnings: list[str] = []
    max_iterations_reached: bool = False
    judge_summary: str | None = None
