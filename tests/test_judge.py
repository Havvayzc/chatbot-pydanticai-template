"""Schneller Test: Gemini-Judge ohne Generator."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bpmn_pipeline.judge import judge_bpmn

TRANSCRIPT = "Der Kunde stellt einen Antrag. Der Mitarbeiter prüft den Antrag und genehmigt oder lehnt ihn ab. Der Kunde wird informiert."

XML = """<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions xmlns:bpmn2="http://www.omg.org/spec/BPMN/20100524/MODEL" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn2:process id="Process_1" isExecutable="false">
    <bpmn2:startEvent id="Start_1" name="Antrag eingegangen"/>
    <bpmn2:endEvent id="End_1" name="Kunde informiert"/>
  </bpmn2:process>
</bpmn2:definitions>"""


async def main():
    print("Teste Gemini-Judge...")
    try:
        result = await judge_bpmn(TRANSCRIPT, XML)
        print(f"OK — {len(result.findings)} Findings, kritisch: {result.has_critical_findings()}")
        for f in result.findings:
            print(f"  [{f.dimension}] critical={f.critical}: {f.description[:80]}")
    except Exception as e:
        print(f"FEHLER: {e}")


asyncio.run(main())
