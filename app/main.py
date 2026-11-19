"""HTTP API + static web app.

Run:  uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import logging

import anthropic
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .core import speech
from .core.actions import Actions, Session
from .core.domains import load_registry
from .core.forms import render_application_html, t
from .core.offline_agent import OfflineAgent
from .core.tracker import Tracker

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("velan")

registry = load_registry(config.DOMAINS_DIR, config.ENABLED_DOMAINS)
tracker = Tracker(config.DB_PATH)
actions = Actions(registry, tracker)
offline_agent = OfflineAgent(actions)
claude_agent = None
if config.use_claude():
    from .core.claude_agent import ClaudeAgent

    claude_agent = ClaudeAgent(actions, config.MODEL)

sessions: dict[str, Session] = {}

app = FastAPI(title="Velan — voice-first government & farm helper")


class NewSession(BaseModel):
    lang: str = config.DEFAULT_LANG
    user_id: str = "demo-user"


class ChatIn(BaseModel):
    session_id: str
    text: str
    lang: str | None = None


class TTSIn(BaseModel):
    text: str
    lang: str = config.DEFAULT_LANG


def _session(session_id: str) -> Session:
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(404, "session not found — start a new one")
    return s


@app.get("/api/config")
def get_config():
    return {
        "agent": "claude" if claude_agent else "offline",
        "model": config.MODEL if claude_agent else None,
        "server_speech": speech.enabled(),
        "languages": config.LANGUAGES,
        "default_lang": config.DEFAULT_LANG,
        "domains": {k: {"name": v.get("name"), "description": v.get("description")} for k, v in registry.domains.items()},
    }


@app.get("/api/services")
def get_services(lang: str = "en"):
    return [
        {"id": s.id, "domain": s.domain, "title": t(s.title, lang), "form": s.form,
         "example": t(registry.domains[s.domain].get("examples", {}).get(s.id, ""), lang)}
        for s in registry.services.values()
    ]


@app.post("/api/session")
def new_session(body: NewSession):
    s = Session(lang=body.lang if body.lang in config.LANGUAGES else config.DEFAULT_LANG, user_id=body.user_id)
    sessions[s.id] = s
    return {"session_id": s.id, "greeting": offline_agent.respond(s, "")}


@app.post("/api/chat")
def chat(body: ChatIn):
    s = _session(body.session_id)
    if body.lang in config.LANGUAGES and body.lang != s.lang:
        s.lang = body.lang
    s.events = []
    agent_used = "offline"
    try:
        if claude_agent:
            reply = claude_agent.respond(s, body.text)
            agent_used = "claude"
        else:
            reply = offline_agent.respond(s, body.text)
    except (anthropic.APIConnectionError, anthropic.RateLimitError, anthropic.InternalServerError) as e:
        # keep the conversation alive on flaky networks: answer this turn offline
        log.warning("Claude unavailable (%s); answering offline", type(e).__name__)
        reply = offline_agent.respond(s, body.text)
    except anthropic.APIStatusError as e:
        log.error("Claude API error %s: %s", e.status_code, e.message)
        raise HTTPException(502, "assistant error") from e
    return {
        "reply": reply,
        "agent": agent_used,
        "events": s.events,
        "form": s.form.to_state(s.lang) if s.form else None,
    }


@app.post("/api/stt")
async def stt(audio: UploadFile = File(...), lang: str = Form(config.DEFAULT_LANG)):
    if not speech.enabled():
        raise HTTPException(501, "server speech-to-text not configured; use browser recognition")
    data = await audio.read()
    return await speech.transcribe(data, audio.filename or "audio.webm", audio.content_type or "audio/webm", lang)


@app.post("/api/tts")
async def tts(body: TTSIn):
    if not speech.enabled():
        raise HTTPException(501, "server text-to-speech not configured; use browser voices")
    audio = await speech.synthesize(body.text, body.lang)
    return Response(content=audio, media_type="audio/wav")


@app.get("/api/applications")
def applications(user_id: str = "demo-user"):
    return tracker.list(user_id)


@app.get("/api/applications/{app_id}/print", response_class=HTMLResponse)
def print_application(app_id: str):
    a = tracker.get(app_id)
    if not a:
        raise HTTPException(404, "application not found")
    form = registry.forms[a["form_id"]]
    return render_application_html(form, a["values"], a["id"], a["created_at"])


@app.get("/")
def index():
    return FileResponse(config.WEB_DIR / "index.html")


app.mount("/", StaticFiles(directory=config.WEB_DIR), name="web")
