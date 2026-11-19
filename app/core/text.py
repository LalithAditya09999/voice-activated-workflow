"""Text helpers for spoken, multilingual, code-mixed input."""
from __future__ import annotations

import re
import unicodedata

# Tamil and Devanagari digits -> ASCII
_DIGIT_MAP = {}
for i, ch in enumerate("०१२३४५६७८९"):
    _DIGIT_MAP[ord(ch)] = str(i)
for i, ch in enumerate("௦௧௨௩௪௫௬௭௮௯"):
    _DIGIT_MAP[ord(ch)] = str(i)

YES_WORDS = {
    "yes", "yeah", "yep", "ok", "okay", "correct", "right", "sure", "confirm", "submit", "haan", "ha", "han",
    "ji", "theek", "sahi", "aama", "aamam", "sari", "seri",
    "हाँ", "हां", "हा", "जी", "ठीक", "सही", "बिल्कुल",
    "ஆமா", "ஆமாம்", "ஆம்", "சரி", "ஓகே", "சரிதான்",
}
NO_WORDS = {
    "no", "nope", "wrong", "incorrect", "nahi", "nahin", "galat", "illa", "illai", "venda",
    "नहीं", "नही", "ना", "गलत",
    "இல்லை", "இல்ல", "வேண்டாம்", "தவறு",
}
CANCEL_WORDS = {
    "cancel", "stop", "quit", "exit", "band", "radd", "ruko",
    "रद्द", "बंद", "रुको", "छोड़ो",
    "நிறுத்து", "ரத்து", "விடு",
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = text.translate(_DIGIT_MAP)
    return text.strip()


_TOKEN_RE = re.compile(r"[\w஀-௿ऀ-ॿ]+", re.UNICODE)


def tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(normalize(text))]


def _has_any(text: str, words: set[str]) -> bool:
    toks = set(tokens(text))
    if toks & words:
        return True
    low = normalize(text).lower()
    # Indic words can arrive with suffixes attached ("சரிதான்", "हाँजी"), so also
    # check prefixes for non-ASCII vocabulary.
    return any(not w.isascii() and any(t.startswith(w) for t in toks) for w in words) or low in words


def is_yes(text: str) -> bool:
    return _has_any(text, YES_WORDS) and not _has_any(text, NO_WORDS)


def is_no(text: str) -> bool:
    return _has_any(text, NO_WORDS)


def is_cancel(text: str) -> bool:
    return _has_any(text, CANCEL_WORDS)


def digits_only(text: str) -> str:
    return re.sub(r"\D", "", normalize(text))


_NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def first_number(text: str) -> float | None:
    text = normalize(text).replace(",", "")
    low = text.lower()
    m = _NUM_RE.search(text)
    if m:
        return float(m.group())
    # very small vocabulary for common spoken fractions/numbers
    words = {
        "half": 0.5, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "ten": 10,
        "aadha": 0.5, "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5,
        "आधा": 0.5, "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "पाँच": 5,
        "அரை": 0.5, "ஒன்று": 1, "ஒரு": 1, "இரண்டு": 2, "ரெண்டு": 2, "மூன்று": 3, "நான்கு": 4, "ஐந்து": 5,
    }
    for tok in tokens(low):
        if tok in words:
            return float(words[tok])
    return None
