"""Schema-driven form engine.

A form is plain JSON (see domains/*/forms). The engine knows how to:
  * ask for the next missing field in the user's language
  * validate + normalise spoken answers (digits in any script, yes/no, choices)
  * mask sensitive values (Aadhaar) before storing
  * read the whole form back for confirmation before submission
  * render a printable application
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from .text import digits_only, first_number, is_no, is_yes, normalize, tokens


class FieldError(ValueError):
    """Raised when a value doesn't pass validation. Message is a key into MESSAGES."""

    def __init__(self, key: str, **params):
        super().__init__(key)
        self.key = key
        self.params = params


MESSAGES = {
    "required": {"en": "I need this detail.", "ta": "இந்த விவரம் தேவை.", "hi": "यह जानकारी ज़रूरी है।"},
    "phone": {"en": "A mobile number has 10 digits.", "ta": "மொபைல் எண் 10 இலக்கங்கள் இருக்க வேண்டும்.", "hi": "मोबाइल नंबर 10 अंकों का होता है।"},
    "aadhaar": {"en": "Aadhaar has 12 digits.", "ta": "ஆதார் எண் 12 இலக்கங்கள்.", "hi": "आधार नंबर 12 अंकों का होता है।"},
    "number": {"en": "Please say a number.", "ta": "ஒரு எண்ணைச் சொல்லுங்கள்.", "hi": "कृपया एक संख्या बताइए।"},
    "range": {"en": "That number looks wrong (expected {min}–{max}).", "ta": "அந்த எண் சரியாகத் தெரியவில்லை ({min}–{max}).", "hi": "यह संख्या सही नहीं लगती ({min}–{max})।"},
    "choice": {"en": "Please choose one of: {options}.", "ta": "இவற்றில் ஒன்றைச் சொல்லுங்கள்: {options}.", "hi": "इनमें से एक चुनें: {options}।"},
    "yesno": {"en": "Please answer yes or no.", "ta": "ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.", "hi": "हाँ या नहीं में जवाब दें।"},
    "date": {"en": "Please say the date, like 12-11-2026 or 'yesterday'.", "ta": "தேதியைச் சொல்லுங்கள், உதா. 12-11-2026 அல்லது 'நேற்று'.", "hi": "तारीख बताइए, जैसे 12-11-2026 या 'कल'।"},
    "date_future": {"en": "That date is in the future.", "ta": "அந்தத் தேதி இன்னும் வரவில்லை.", "hi": "यह तारीख भविष्य की है।"},
    "pattern": {"en": "That doesn't look right.", "ta": "அது சரியாகத் தெரியவில்லை.", "hi": "यह सही नहीं लगता।"},
}


def t(obj: dict | str, lang: str) -> str:
    """Pick the language variant of a multilingual string, falling back to English."""
    if isinstance(obj, str):
        return obj
    return obj.get(lang) or obj.get("en") or next(iter(obj.values()), "")


def message(key: str, lang: str, **params) -> str:
    return t(MESSAGES[key], lang).format(**params)


def _parse_date(raw: str) -> date:
    text = normalize(raw).lower()
    today = date.today()
    rel = {
        ("today", "aaj", "आज", "இன்று", "இன்னைக்கு"): 0,
        ("yesterday", "kal", "कल", "நேற்று", "நேத்து"): 1,
        ("day before yesterday", "parson", "परसों", "முந்தாநாள்"): 2,
    }
    for words, delta in sorted(rel.items(), key=lambda kv: -kv[1]):
        if any(w in text for w in words):
            return today - timedelta(days=delta)
    m = re.search(r"(\d{1,2})\s*[-/. ]\s*(\d{1,2})\s*[-/. ]\s*(\d{2,4})", text)
    if m:
        d, mth, y = (int(x) for x in m.groups())
        if y < 100:
            y += 2000
        return date(y, mth, d)
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        return date(*(int(x) for x in m.groups()))
    raise FieldError("date")


def coerce(field_def: dict, raw, lang: str = "en"):
    """Validate and normalise a single answer. Returns the stored value."""
    ftype = field_def.get("type", "text")
    if raw is None or (isinstance(raw, str) and not normalize(raw)):
        raise FieldError("required")
    if isinstance(raw, bool):
        if ftype == "yesno":
            return raw
        raw = str(raw)
    elif isinstance(raw, (int, float)):
        raw = float(raw) if ftype == "number" else str(raw)
    if not isinstance(raw, float):
        raw = normalize(str(raw))

    if ftype == "text":
        value = re.sub(r"\s+", " ", raw).strip(" .,")
        if len(value) < field_def.get("min_length", 1):
            raise FieldError("required")
        if field_def.get("pattern") and not re.fullmatch(field_def["pattern"], value):
            raise FieldError("pattern")
        return value

    if ftype == "phone":
        d = digits_only(raw)
        if len(d) == 12 and d.startswith("91"):
            d = d[2:]
        if len(d) != 10 or d[0] not in "6789":
            raise FieldError("phone")
        return d

    if ftype == "aadhaar":
        d = digits_only(raw)
        if len(d) != 12:
            raise FieldError("aadhaar")
        # privacy: never keep the full number, only enough to match documents
        return "XXXX-XXXX-" + d[-4:]

    if ftype == "number":
        value = raw if isinstance(raw, float) else first_number(raw)
        if value is None:
            raise FieldError("number")
        lo, hi = field_def.get("min"), field_def.get("max")
        if (lo is not None and value < lo) or (hi is not None and value > hi):
            raise FieldError("range", min=lo, max=hi)
        return int(value) if float(value).is_integer() else round(value, 2)

    if ftype == "yesno":
        if is_yes(raw):
            return True
        if is_no(raw):
            return False
        raise FieldError("yesno")

    if ftype == "choice":
        options = field_def["options"]
        low = raw.lower()
        toks = set(tokens(raw))
        for opt in options:
            if low == opt["value"].lower():
                return opt["value"]
        for opt in options:
            for alias in [opt["value"], *opt.get("aliases", []), *[v for v in opt.get("label", {}).values()]]:
                a = alias.lower()
                if (a.isascii() and " " not in a and a in toks) or ((not a.isascii() or " " in a) and a in low):
                    return opt["value"]
        raise FieldError("choice", options=", ".join(t(o.get("label", o["value"]), lang) for o in options))

    if ftype == "date":
        d = _parse_date(raw)
        if field_def.get("past_only") and d > date.today():
            raise FieldError("date_future")
        return d.isoformat()

    raise ValueError(f"Unknown field type {ftype}")


def display_value(field_def: dict, value, lang: str) -> str:
    if value is None:
        return "—"
    ftype = field_def.get("type")
    if ftype == "yesno":
        return {"en": ("Yes", "No"), "ta": ("ஆம்", "இல்லை"), "hi": ("हाँ", "नहीं")}[lang if lang in ("en", "ta", "hi") else "en"][0 if value else 1]
    if ftype == "choice":
        for opt in field_def["options"]:
            if opt["value"] == value:
                return t(opt.get("label", value), lang)
    if ftype == "phone":
        return " ".join([value[:5], value[5:]])
    return str(value)


@dataclass
class FormSession:
    form: dict
    values: dict = field(default_factory=dict)
    awaiting_confirmation: bool = False
    editing_field: str | None = None

    @property
    def id(self) -> str:
        return self.form["id"]

    @property
    def fields(self) -> list[dict]:
        return self.form["fields"]

    def field(self, field_id: str) -> dict:
        for f in self.fields:
            if f["id"] == field_id:
                return f
        raise KeyError(field_id)

    def _applicable(self, f: dict) -> bool:
        cond = f.get("ask_if")
        if not cond:
            return True
        return self.values.get(cond["field"]) in cond.get("in", [cond.get("equals")])

    def missing(self) -> list[dict]:
        return [f for f in self.fields if self._applicable(f) and f.get("required", True) and f["id"] not in self.values]

    def next_field(self) -> dict | None:
        if self.editing_field:
            return self.field(self.editing_field)
        m = self.missing()
        return m[0] if m else None

    def set(self, field_id: str, raw, lang: str = "en"):
        f = self.field(field_id)
        value = coerce(f, raw, lang)
        self.values[field_id] = value
        if self.editing_field == field_id:
            self.editing_field = None
        # dropping values whose ask_if no longer holds keeps the read-back honest
        for other in self.fields:
            if other["id"] in self.values and not self._applicable(other):
                del self.values[other["id"]]
        return value

    def question(self, f: dict, lang: str) -> str:
        q = t(f.get("question", f.get("label", f["id"])), lang)
        if f.get("type") == "choice":
            opts = " / ".join(t(o.get("label", o["value"]), lang) for o in f["options"])
            q = f"{q} ({opts})"
        return q

    def progress(self) -> tuple[int, int]:
        applicable = [f for f in self.fields if self._applicable(f) and f.get("required", True)]
        done = [f for f in applicable if f["id"] in self.values]
        return len(done), len(applicable)

    def readback(self, lang: str) -> list[tuple[str, str]]:
        return [
            (t(f.get("label", f["id"]), lang), display_value(f, self.values[f["id"]], lang))
            for f in self.fields
            if f["id"] in self.values
        ]

    def find_field_mentioned(self, text: str, lang: str) -> dict | None:
        low = normalize(text).lower()
        for f in self.fields:
            if f["id"] not in self.values:
                continue
            labels = [*f.get("label", {}).values(), f["id"].replace("_", " "), *f.get("aliases", [])]
            if any(lbl and lbl.lower() in low for lbl in labels):
                return f
        return None

    def to_state(self, lang: str) -> dict:
        done, total = self.progress()
        nxt = self.next_field()
        return {
            "form_id": self.id,
            "title": t(self.form["title"], lang),
            "fields": [
                {
                    "id": f["id"],
                    "label": t(f.get("label", f["id"]), lang),
                    "value": display_value(f, self.values.get(f["id"]), lang) if f["id"] in self.values else None,
                    "current": nxt is not None and nxt["id"] == f["id"],
                }
                for f in self.fields
                if self._applicable(f)
            ],
            "progress": {"done": done, "total": total},
            "awaiting_confirmation": self.awaiting_confirmation,
            "documents": [t(d, lang) for d in self.form.get("documents", [])],
        }


def render_application_html(form: dict, values: dict, app_id: str, created_at: str) -> str:
    """Printable English application (official forms are usually filled in English)."""
    rows = "".join(
        f"<tr><th>{html.escape(t(f.get('label', f['id']), 'en'))}</th>"
        f"<td>{html.escape(display_value(f, values[f['id']], 'en'))}</td></tr>"
        for f in form["fields"]
        if f["id"] in values
    )
    docs = "".join(f"<li>☐ {html.escape(t(d, 'en'))}</li>" for d in form.get("documents", []))
    created = datetime.fromisoformat(created_at).strftime("%d %b %Y")
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(app_id)}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:760px;margin:24px auto;padding:0 16px;color:#111}}
h1{{font-size:20px;margin-bottom:4px}}table{{width:100%;border-collapse:collapse;margin:16px 0}}
th,td{{border:1px solid #999;padding:8px;text-align:left;vertical-align:top}}th{{width:40%;background:#f3f3f3}}
.meta{{color:#444;font-size:14px}}.note{{font-size:12px;color:#555;border-top:1px solid #ccc;padding-top:8px;margin-top:24px}}
@media print{{button{{display:none}}}}</style></head><body>
<button onclick="window.print()">Print</button>
<h1>{html.escape(t(form['title'], 'en'))}</h1>
<div class="meta">Reference: <b>{html.escape(app_id)}</b> · Prepared: {created}<br>
Submit to: {html.escape(t(form.get('submit_to', ''), 'en'))}</div>
<table>{rows}</table>
<h2 style="font-size:16px">Documents to attach</h2><ul style="list-style:none;padding-left:0">{docs}</ul>
<p>Applicant signature / thumb impression: ______________________</p>
<div class="note">Prepared with a voice assistant from the applicant's spoken answers and read back to them for confirmation.
This is a draft to carry to the office or e-Sevai centre; it is not an official submission. Aadhaar is masked.</div>
</body></html>"""
