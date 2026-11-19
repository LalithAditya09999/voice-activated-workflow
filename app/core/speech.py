"""Optional server-side Indic speech via Sarvam AI.

Without SARVAM_API_KEY the web app uses the browser's own speech recognition and voices
(works well in Chrome on Android for ta-IN / hi-IN). Sarvam gives better accuracy for
code-mixed speech and natural Indian voices.

Endpoint shapes follow Sarvam's public REST docs; check https://docs.sarvam.ai if the
models or field names have changed (they're isolated here so that's a one-file fix).
"""
from __future__ import annotations

import base64

import httpx2 as httpx

from ..config import LANGUAGES, SARVAM_API_KEY

BASE = "https://api.sarvam.ai"
STT_MODEL = "saarika:v2.5"
TTS_MODEL = "bulbul:v2"
TTS_SPEAKER = "anushka"


def enabled() -> bool:
    return bool(SARVAM_API_KEY)


def _headers() -> dict:
    return {"api-subscription-key": SARVAM_API_KEY}


async def transcribe(audio: bytes, filename: str, content_type: str, lang: str | None) -> dict:
    data = {"model": STT_MODEL, "language_code": LANGUAGES[lang]["bcp47"] if lang in LANGUAGES else "unknown"}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BASE}/speech-to-text", headers=_headers(), data=data,
                              files={"file": (filename, audio, content_type)})
        r.raise_for_status()
        body = r.json()
    return {"text": body.get("transcript", ""), "language": body.get("language_code")}


async def synthesize(text: str, lang: str) -> bytes:
    payload = {
        "text": text[:1500],
        "target_language_code": LANGUAGES.get(lang, LANGUAGES["en"])["bcp47"],
        "model": TTS_MODEL,
        "speaker": TTS_SPEAKER,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BASE}/text-to-speech", headers=_headers(), json=payload)
        r.raise_for_status()
        audios = r.json().get("audios", [])
    return base64.b64decode(audios[0]) if audios else b""
