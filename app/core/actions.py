"""The actions the assistant can take. Both agents (Claude and offline) call these,
so behaviour like validation, read-back and submission is identical in both modes."""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field

from .domains import Registry
from .eligibility import evaluate
from .forms import FieldError, FormSession, message, t
from .tracker import Tracker


@dataclass
class Session:
    id: str = field(default_factory=lambda: secrets.token_urlsafe(12))
    user_id: str = "demo-user"
    lang: str = "ta"
    form: FormSession | None = None
    profile: dict = field(default_factory=dict)
    pending_service: str | None = None   # service we offered to start, awaiting yes/no
    request_text: str = ""                # the sentence that started the current request (for prefilling)
    farming_style: str = "both"           # "organic" | "conventional" | "both" — what advice to lead with
    messages: list = field(default_factory=list)  # Claude conversation history
    events: list = field(default_factory=list)    # UI events for the current turn

    def emit(self, kind: str, data) -> None:
        self.events.append({"type": kind, "data": data})


def spoken_digits(value) -> str:
    """'9876543210' -> '9 8 7 6 5, 4 3 2 1 0' so a voice reads it digit by digit."""
    chars = [c for c in str(value).replace("XXXX-XXXX-", "") if c.isalnum() or c in "/-"]
    groups = [" ".join(chars[i:i + 5]) for i in range(0, len(chars), 5)]
    return ", ".join(groups)


class Actions:
    def __init__(self, registry: Registry, tracker: Tracker):
        self.reg = registry
        self.tracker = tracker

    # ---------------- knowledge ----------------
    def search_knowledge(self, s: Session, query: str, k: int = 3) -> dict:
        hits = self.reg.search(query, k)
        s.emit("sources", [{"id": d.id, "title": d.title, "source": d.source, "verified": d.verified} for d, _ in hits])
        return {
            "results": [
                {"id": d.id, "title": d.title, "summary": t(d.summary, s.lang) if d.summary else "",
                 "content": d.body, "source": d.source, "verified": d.verified,
                 "last_checked": d.last_checked or "not yet checked against the official source"}
                for d, _ in hits
            ]
        }

    def list_services(self, s: Session) -> dict:
        return {
            "services": [
                {"id": svc.id, "domain": svc.domain, "title": t(svc.title, s.lang), "has_form": bool(svc.form)}
                for svc in self.reg.services.values()
            ]
        }

    def explain_service(self, s: Session, service_id: str) -> dict:
        svc = self.reg.services.get(service_id)
        if not svc:
            return {"error": f"unknown service {service_id}"}
        docs = [self.reg.knowledge[k] for k in svc.knowledge]
        form = self.reg.forms.get(svc.form) if svc.form else None
        s.emit("sources", [{"id": d.id, "title": d.title, "source": d.source, "verified": d.verified} for d in docs])
        return {
            "service": svc.id,
            "title": t(svc.title, s.lang),
            "summary": [t(d.summary, s.lang) for d in docs if d.summary],
            "content": [d.body for d in docs],
            "documents": [t(x, s.lang) for x in form.get("documents", [])] if form else [],
            "submit_to": t(form.get("submit_to", ""), s.lang) if form else "",
            "form_id": svc.form,
            "deadline_note": t(form.get("deadline_note", ""), s.lang) if form else "",
        }

    # ---------------- forms ----------------
    def start_form(self, s: Session, form_id: str) -> dict:
        form = self.reg.forms.get(form_id)
        if not form:
            return {"error": f"unknown form {form_id}", "available": list(self.reg.forms)}
        prefill = {}
        if s.form and s.form.id != form_id:
            prefill = dict(s.form.values)
        s.form = FormSession(form=form)
        # carry over details the user already gave (name, phone, village...) for any field ids that match
        for f in form["fields"]:
            if f["id"] in prefill and f.get("reuse", True):
                s.form.values[f["id"]] = prefill[f["id"]]
        s.pending_service = None
        s.emit("form", s.form.to_state(s.lang))
        return self.form_status(s)

    def set_form_fields(self, s: Session, values: dict) -> dict:
        if not s.form:
            return {"error": "no active form; call start_form first"}
        saved, errors = {}, {}
        for fid, raw in values.items():
            try:
                saved[fid] = s.form.set(fid, raw, s.lang)
            except KeyError:
                errors[fid] = "unknown field"
            except FieldError as e:
                errors[fid] = message(e.key, s.lang, **e.params)
        s.form.awaiting_confirmation = False
        s.emit("form", s.form.to_state(s.lang))
        out = self.form_status(s)
        out.update({"saved": saved, "errors": errors})
        digits = {fid: spoken_digits(v) for fid, v in saved.items() if s.form.field(fid).get("confirm_digits")}
        if digits:
            out["confirm_digits"] = digits
            out["instruction"] = ("Read these values back digit by digit and ask the user to confirm before "
                                  "moving on; if they say it is wrong, ask for it again.")
        return out

    def form_status(self, s: Session) -> dict:
        if not s.form:
            return {"active": False}
        nxt = s.form.next_field()
        return {
            "active": True,
            "form_id": s.form.id,
            "title": t(s.form.form["title"], s.lang),
            "collected": dict(s.form.readback(s.lang)),
            "next_field": None if not nxt else {
                "id": nxt["id"], "type": nxt.get("type", "text"),
                "question": s.form.question(nxt, s.lang),
                "options": [o["value"] for o in nxt.get("options", [])],
            },
            "remaining": [f["id"] for f in s.form.missing()],
            "ready_for_confirmation": nxt is None,
        }

    def request_confirmation(self, s: Session) -> dict:
        if not s.form:
            return {"error": "no active form"}
        if s.form.next_field():
            return {"error": "form incomplete", **self.form_status(s)}
        s.form.awaiting_confirmation = True
        s.emit("form", s.form.to_state(s.lang))
        return {"readback": s.form.readback(s.lang), "instruction": "Read every item back to the user and ask them to confirm."}

    def edit_field(self, s: Session, field_id: str) -> dict:
        if not s.form:
            return {"error": "no active form"}
        f = s.form.field(field_id)
        s.form.values.pop(field_id, None)
        s.form.editing_field = field_id
        s.form.awaiting_confirmation = False
        s.emit("form", s.form.to_state(s.lang))
        return {"ask": s.form.question(f, s.lang)}

    def submit_form(self, s: Session, user_confirmed: bool) -> dict:
        if not s.form:
            return {"error": "no active form"}
        if s.form.next_field():
            return {"error": "form incomplete", **self.form_status(s)}
        if not (user_confirmed and s.form.awaiting_confirmation):
            return {"error": "read the details back with request_confirmation and get an explicit yes first"}
        form, values = s.form.form, dict(s.form.values)
        s.form = None
        s.emit("form", None)

        if form.get("kind") == "profile":
            s.profile.update(values)
            return self.check_eligibility(s)

        app = self.tracker.create(s.user_id, form, values, next_step=t(form.get("next_step", ""), "en"))
        app_view = {
            "id": app["id"], "title": t(form["title"], s.lang), "follow_up_on": app["follow_up_on"],
            "print_url": f"/api/applications/{app['id']}/print",
            "submit_to": t(form.get("submit_to", ""), s.lang),
            "next_step": t(form.get("next_step", ""), s.lang),
            "documents": [t(d, s.lang) for d in form.get("documents", [])],
            "deadline_note": t(form.get("deadline_note", ""), s.lang),
        }
        s.emit("application", app_view)
        return {"submitted": True, **app_view}

    def cancel_form(self, s: Session) -> dict:
        s.form = None
        s.pending_service = None
        s.emit("form", None)
        return {"cancelled": True}

    def set_farming_preference(self, s: Session, style: str) -> dict:
        if style not in ("organic", "conventional", "both"):
            return {"error": "style must be organic, conventional or both"}
        s.farming_style = style
        s.emit("preference", style)
        return {"farming_style": style}

    # ---------------- eligibility ----------------
    def check_eligibility(self, s: Session, profile: dict | None = None) -> dict:
        if profile:
            s.profile.update(profile)
        results = evaluate(self.reg.schemes, s.profile, s.lang)
        s.emit("eligibility", results)
        return {"profile": s.profile, "results": results}

    # ---------------- tracking ----------------
    def list_applications(self, s: Session) -> dict:
        apps = self.tracker.list(s.user_id)
        s.emit("applications", apps)
        return {"applications": [
            {"id": a["id"], "title": a["title"], "status": a["status"], "created_at": a["created_at"],
             "follow_up_on": a["follow_up_on"], "overdue": a["overdue"]}
            for a in apps
        ]}
