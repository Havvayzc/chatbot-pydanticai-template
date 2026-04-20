"""
BPMN Pipeline — Transcript to BPMN 2.0 Model
Bachelor thesis: Sare Yazici, HKA

Pipeline stages:
  1. Generator   (Claude Opus 4.6)  — produces BPMN 2.0 XML from transcript
  2. Schema check (bpmn-moddle)     — ensures XML is well-formed and all refs valid
  3. Soundness   (bpmnlint)         — structural rules (start/end events, gateways, ...)
  4. Judge       (Gemini)           — semantic quality: coverage, faithfulness, order, actors
  5. Auto-layout (bpmn-auto-layout) — adds visual coordinates deterministically
"""
