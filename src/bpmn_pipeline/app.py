"""
FastAPI app for the BPMN Pipeline.

Endpoints:
  POST /generate   — run the full pipeline on a transcript
  GET  /health     — health check

Run with:
  uv run uvicorn bpmn_pipeline.app:app --reload --port 8001
"""

import logging
import traceback
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .pipeline import run_pipeline

logger = logging.getLogger(__name__)

_STATIC = Path(__file__).parent / "static"

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="BPMN Pipeline API",
    description=(
        "Converts censored meeting transcripts into validated BPMN 2.0 models "
        "using Claude Opus 4.6 (generator) and Gemini (semantic judge)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return all unhandled errors as JSON so the browser can display them."""
    tb = traceback.format_exc()
    logger.error(f"Unhandled error on {request.url}: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {exc}"},
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(_STATIC / "index.html"))


class GenerateRequest(BaseModel):
    transcript: str


class GenerateResponse(BaseModel):
    success: bool
    bpmn_xml: str
    iterations: int
    warnings: list[str]
    max_iterations_reached: bool
    judge_summary: str | None


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """
    Run the full pipeline: transcript → validated BPMN 2.0 XML with layout.

    - Iterates up to MAX_ITERATIONS times (default: 3).
    - Each iteration: Generate → Schema check → Soundness → Semantic judge → Layout.
    - Returns the final BPMN XML plus metadata (iteration count, warnings, judge summary).
    """
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty.")

    try:
        result = await run_pipeline(request.transcript)
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error(f"Pipeline error: {exc}\n{tb}")
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}") from exc

    return GenerateResponse(
        success=result.success,
        bpmn_xml=result.bpmn_xml,
        iterations=result.iterations,
        warnings=result.warnings,
        max_iterations_reached=result.max_iterations_reached,
        judge_summary=result.judge_summary,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
