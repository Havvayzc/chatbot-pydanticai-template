"""
Standalone-Test für den Generator.

Verwendung:
  uv run python tests/test_generator.py
  uv run python tests/test_generator.py --transcript pfad/zum/transkript.txt
  uv run python tests/test_generator.py --out ergebnis.bpmn

Das erzeugte XML wird auf stdout ausgegeben (und optional in eine Datei gespeichert).
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")

SAMPLE_TRANSCRIPT = """
Ein Kunde sendet eine Anfrage an den Spezialfertiger.
Der Vertrieb erfasst die Anfrage und leitet sie an den Ingenieur weiter.
Der Ingenieur prüft die Machbarkeit. Ist es nicht machbar, sendet der Vertrieb eine Absage.
Ist es machbar, erstellt der Ingenieur einen Fertigungsplan und eine Materialliste.
Anschließend erstellt der Vertrieb ein Angebot und sendet es an den Kunden.
Der Kunde prüft das Angebot. Akzeptiert er es, erteilt er den Auftrag.
Lehnt er ab, endet der Prozess.
Nach Auftragserteilung bestellt der Einkauf die benötigten Teile.
Die Produktion fertigt das Gerät und prüft die Qualität.
Danach verpackt und liefert der Versand das Gerät an den Kunden.
Die Verwaltung erstellt die Rechnung. Der Kunde bezahlt.
"""


async def main() -> None:
    parser = argparse.ArgumentParser(description="Test des BPMN-Generators")
    parser.add_argument("--transcript", help="Pfad zu einer Transkript-Textdatei")
    parser.add_argument("--out", help="Ausgabedatei für das XML (optional)")
    args = parser.parse_args()

    if args.transcript:
        transcript = Path(args.transcript).read_text(encoding="utf-8")
        print(f"Transkript geladen: {len(transcript)} Zeichen", file=sys.stderr)
    else:
        transcript = SAMPLE_TRANSCRIPT
        print("Kein Transkript angegeben — nutze eingebautes Beispiel.", file=sys.stderr)

    from bpmn_pipeline.generator import generate_bpmn

    xml = await generate_bpmn(transcript)

    if args.out:
        Path(args.out).write_text(xml, encoding="utf-8")
        print(f"XML gespeichert: {args.out}", file=sys.stderr)
    else:
        print(xml)


if __name__ == "__main__":
    asyncio.run(main())
