"""
FastAPI-App für die BPMN-Pipeline.

GET  /          → UI (index.html)
POST /generate  → Transkript → BPMN-XML als Download
"""

import logging

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from .generator import generate_bpmn

logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")

app = FastAPI(title="BPMN Pipeline")

app.mount(
    "/static",
    StaticFiles(directory=str(__import__("pathlib").Path(__file__).parent / "static")),
    name="static",
)


@app.get("/", response_class=HTMLResponse)
async def index():
    html = (__import__("pathlib").Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.post("/generate")
async def generate(transcript: str = Form(...)):
    if not transcript.strip():
        raise HTTPException(status_code=400, detail="Transkript darf nicht leer sein.")

    try:
        xml = await generate_bpmn(transcript)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return Response(
        content=xml.encode("utf-8"),
        media_type="application/xml",
        headers={"Content-Disposition": 'attachment; filename="process.bpmn"'},
    )
