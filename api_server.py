from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import os, time

app = FastAPI(title="OLIS Live Shadow Dashboard API")

API_KEY = os.getenv("OLIS_API_KEY", "CHANGE_ME")
LATEST = {"capture_id": 0, "fixtures": [], "updated_at": None, "summary": {}}

class Capture(BaseModel):
    capture_id: int
    fixtures: list
    summary: dict = {}
    updated_at: Optional[str] = None

@app.get("/api/health")
def health():
    return {"status": "ok", "capture_id": LATEST["capture_id"]}

@app.get("/api/live")
def live():
    return LATEST

@app.post("/api/live")
def publish(capture: Capture, x_olis_key: Optional[str] = Header(default=None)):
    if x_olis_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    global LATEST
    LATEST = capture.model_dump()
    LATEST["updated_at"] = LATEST.get("updated_at") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return {"ok": True, "capture_id": LATEST["capture_id"]}

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h2>OLIS Dashboard API</h2><p>Dashboard endpoint: /api/live</p>"
