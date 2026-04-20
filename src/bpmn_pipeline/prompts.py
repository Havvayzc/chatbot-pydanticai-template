"""
Loads system prompts from editable .txt files in the prompts/ directory.

To adjust the generator or judge behaviour, simply edit:
  src/bpmn_pipeline/prompts/generator.txt
  src/bpmn_pipeline/prompts/judge.txt

No Python code changes needed — the server picks up changes on restart.
"""

from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load(filename: str) -> str:
    path = _PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


GENERATOR_SYSTEM_PROMPT: str = _load("generator.txt")
JUDGE_SYSTEM_PROMPT: str = _load("judge.txt")
