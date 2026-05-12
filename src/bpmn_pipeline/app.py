"""
FastAPI-App für die BPMN-Pipeline.

GET  /               → UI (index.html)
POST /generate       → startet Pipeline, gibt job_id zurück
GET  /status/{id}    → {"status": "running"|"done"|"error", "detail": "..."}
GET  /download/{id}  → BPMN-XML als Download
"""

import asyncio
import logging
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from .pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")

app = FastAPI(title="BPMN Pipeline")

app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).parent / "static")),
    name="static",
)

_jobs: dict[str, dict] = {}


async def _run_job(job_id: str, transcript: str) -> None:
    try:
        xml = await run_pipeline(transcript)
        _jobs[job_id] = {"status": "done", "xml": xml}
    except Exception as exc:
        _jobs[job_id] = {"status": "error", "detail": str(exc)}


@app.get("/", response_class=HTMLResponse)
async def index():
    html = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.post("/generate")
async def generate(background_tasks: BackgroundTasks, transcript: str = Form(...)):
    if not transcript.strip():
        raise HTTPException(status_code=400, detail="Transkript darf nicht leer sein.")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "running"}
    background_tasks.add_task(_run_job, job_id, transcript)
    return JSONResponse({"job_id": job_id})


@app.get("/status/{job_id}")
async def status(job_id: str):
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job nicht gefunden.")
    if job["status"] == "done":
        return JSONResponse({"status": "done"})
    if job["status"] == "error":
        return JSONResponse({"status": "error", "detail": job.get("detail", "Unbekannter Fehler")})
    return JSONResponse({"status": "running"})


@app.get("/download/{job_id}")
async def download(job_id: str):
    job = _jobs.get(job_id)
    if job is None or job["status"] != "done":
        raise HTTPException(status_code=404, detail="Ergebnis nicht verfügbar.")
    xml = job.pop("xml")
    _jobs.pop(job_id, None)
    return Response(
        content=xml.encode("utf-8"),
        media_type="application/xml",
        headers={"Content-Disposition": 'attachment; filename="process.bpmn"'},
    )
