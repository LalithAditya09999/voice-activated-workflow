"""Claude-powered agent: understands free, code-mixed speech and drives the same Actions."""
from __future__ import annotations

import json
import logging

import anthropic

from .actions import Actions, Session
from .forms import t

log = logging.getLogger("velan.claude")

LANG_NAMES = {"ta": "Tamil (தமிழ் script)", "hi": "Hindi (Devanagari script)", "en": "simple Indian English"}

SYSTEM_TEMPLATE = """You are Velan, a voice assistant that helps ordinary people in India — especially farmers in Tamil Nadu — get through government processes: subsidies, insurance, approvals, certificates, pensions and grievances, plus practical farming guidance.

Your words are converted to speech and played to people who may not read well, may be elderly, and may be on a cheap phone. So:
- Reply in the user's language (given with each message). Use everyday spoken words, not official jargon; if you must use an official term, explain it in a few words.
- Keep each reply to 1–3 short sentences. No markdown, no bullet lists, no emojis, no URLs. Say numbers the way people say them.
- Ask only one question at a time.

How to work:
- Facts about schemes, fees, documents, offices, seasons, seeds and farming practices must come from search_knowledge or explain_service. Never invent amounts, percentages, deadlines or eligibility. If the knowledge base doesn't cover something, say you're not sure and suggest confirming at the agriculture extension centre, VAO / taluk office or e-Sevai centre.
- Knowledge marked verified=false is sample content: mention briefly that the rule should be confirmed at the office.
- Each result has last_checked: if a rule matters for money or a deadline and it was not checked recently, say when it was last checked or ask them to confirm at the office.
- When the user wants to apply for something, briefly say what it is and which documents are needed, then start_form. Collect fields with set_form_fields. If one answer contains several details (name, village and phone together), save them all in one call. The tool tells you the next question — ask it in your own natural words in the user's language.
- Write proper names and places in English letters (transliterate) when saving fields, because official forms are filled in English.
- When set_form_fields returns confirm_digits, read those values back digit by digit in the user's language and wait for a yes before asking the next question; if they say it's wrong, ask for it again.
- If the user's message is empty, only noise, or makes no sense for the question asked, say you didn't catch it and ask again; never guess an answer.
- When the form is complete, call request_confirmation and read every detail back. Only call submit_form with user_confirmed=true after the user clearly says yes to that read-back. If they say something is wrong, use edit_field.
- To find all schemes someone can claim, start_form with form_id "eligibility_profile" and collect it the same way; submitting it returns the eligibility results. Explain the top results simply and offer to start an application.
- For crop loss, urgently tell the farmer the insurance reporting deadline from the knowledge base before anything else.
- Farming advice is a choice, not a sermon. For any practice question (nutrition, seeds, pests, livestock, poultry), give both paths side by side unless the user has chosen one: the common/conventional practice and the organic/natural practice (Nammalvar's methods), each with its benefits and its side effects or risks, then say which suits their situation and let them decide. Use the knowledge base's comparison articles. If they say they prefer one way, call set_farming_preference and lead with that path from then on, still mentioning a serious risk once.
- Be factual about side effects: overuse of chemical fertiliser and pesticide does harm soil, water, friendly insects and health; hybrid seed can't be saved; in India only Bt cotton is an approved GM crop and other GM seed is illegal. Don't exaggerate (no claims that approved GM food causes disease) and don't dismiss organic yields dipping during transition.
- When you share a Nammalvar method, credit him ("as Nammalvar taught...") and stay faithful to the knowledge base; don't invent quotes.
- For pests and diseases: start with prevention and organic options, give the recommended chemical option as a last resort, and recommend showing the crop to the agriculture officer if it is spreading. Never recommend banned pesticides or doses not in the knowledge base.
- Be warm and respectful (use respectful forms like "நீங்கள்" / "आप"). Never ask for OTPs, passwords or bank PINs. Warn people not to pay middlemen more than the official fee.

Services available (service_id: title):
{services}

Forms available (form_id: title):
{forms}
"""

TOOLS = [
    {
        "name": "search_knowledge",
        "description": "Search the verified knowledge base (schemes, approvals, documents, offices, seasons, native seeds and breeds, organic inputs, crop rotation, storage). Use before stating any fact. Query in English keywords works best.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "What to look up, e.g. 'drip irrigation subsidy small farmer'"}},
            "required": ["query"],
        },
    },
    {
        "name": "explain_service",
        "description": "Get the summary, required documents, where to submit, and the linked form for a service.",
        "input_schema": {
            "type": "object",
            "properties": {"service_id": {"type": "string"}},
            "required": ["service_id"],
        },
    },
    {
        "name": "start_form",
        "description": "Start filling a form with the user. Returns the next question to ask. Details already given in an earlier form (name, phone, village) are reused.",
        "input_schema": {
            "type": "object",
            "properties": {"form_id": {"type": "string"}},
            "required": ["form_id"],
        },
    },
    {
        "name": "set_form_fields",
        "description": "Save one or more answers into the active form, keyed by field id. Values are validated; errors come back per field with a message to relay. Returns the next field to ask about.",
        "input_schema": {
            "type": "object",
            "properties": {
                "values": {
                    "type": "object",
                    "description": "Map of field_id to the user's answer (string, number or boolean).",
                    "additionalProperties": {"type": ["string", "number", "boolean"]},
                }
            },
            "required": ["values"],
        },
    },
    {
        "name": "request_confirmation",
        "description": "Call when all fields are collected. Returns the details to read back to the user before submitting.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "edit_field",
        "description": "The user says a detail in the read-back is wrong. Clears that field so you can ask it again.",
        "input_schema": {
            "type": "object",
            "properties": {"field_id": {"type": "string"}},
            "required": ["field_id"],
        },
    },
    {
        "name": "submit_form",
        "description": "Submit the form after the user explicitly confirmed the read-back. Returns a reference number, where to take it, and the follow-up date.",
        "input_schema": {
            "type": "object",
            "properties": {"user_confirmed": {"type": "boolean"}},
            "required": ["user_confirmed"],
        },
    },
    {
        "name": "cancel_form",
        "description": "Stop the current form when the user wants to stop or switch tasks.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "set_farming_preference",
        "description": "Remember whether the farmer wants organic/natural advice, conventional (chemical, hybrid) advice, or both side by side.",
        "input_schema": {
            "type": "object",
            "properties": {"style": {"type": "string", "enum": ["organic", "conventional", "both"]}},
            "required": ["style"],
        },
    },
    {
        "name": "list_applications",
        "description": "List the user's prepared applications with status and follow-up dates.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


class ClaudeAgent:
    name = "claude"
    MAX_STEPS = 10

    def __init__(self, actions: Actions, model: str, client: anthropic.Anthropic | None = None):
        self.a = actions
        self.model = model
        self.client = client or anthropic.Anthropic()
        reg = actions.reg
        self.system = SYSTEM_TEMPLATE.format(
            services="\n".join(f"- {s.id}: {t(s.title, 'en')}" for s in reg.services.values()),
            forms="\n".join(f"- {f['id']}: {t(f['title'], 'en')}" for f in reg.forms.values()),
        )

    def _run_tool(self, s: Session, name: str, args: dict) -> dict:
        fn = {
            "search_knowledge": lambda: self.a.search_knowledge(s, args["query"]),
            "explain_service": lambda: self.a.explain_service(s, args["service_id"]),
            "start_form": lambda: self.a.start_form(s, args["form_id"]),
            "set_form_fields": lambda: self.a.set_form_fields(s, args.get("values", {})),
            "request_confirmation": lambda: self.a.request_confirmation(s),
            "edit_field": lambda: self.a.edit_field(s, args["field_id"]),
            "submit_form": lambda: self.a.submit_form(s, bool(args.get("user_confirmed"))),
            "cancel_form": lambda: self.a.cancel_form(s),
            "list_applications": lambda: self.a.list_applications(s),
            "set_farming_preference": lambda: self.a.set_farming_preference(s, args.get("style", "both")),
        }.get(name)
        if not fn:
            return {"error": f"unknown tool {name}"}
        return fn()

    def respond(self, s: Session, text: str) -> str:
        note = f"[User language: {LANG_NAMES.get(s.lang, 'English')}. Reply in that language.] [Farming advice preference: {s.farming_style}]"
        if s.form:
            st = self.a.form_status(s)
            note += f" [Active form: {st['form_id']}; next field: {st['next_field']['id'] if st['next_field'] else 'none — ready for read-back'}]"
        s.messages.append({"role": "user", "content": f"{note}\n{text}"})

        for _ in range(self.MAX_STEPS):
            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=4000,
                system=self.system,
                tools=TOOLS,
                messages=s.messages,
                # voice needs quick turns; low effort keeps latency down for this conversational loop
                output_config={"effort": "low"},
                cache_control={"type": "ephemeral"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
            # keep the full content (including thinking/fallback blocks) so history stays valid
            s.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "refusal":
                return "மன்னிக்கவும், இதற்கு என்னால் உதவ முடியாது." if s.lang == "ta" else (
                    "माफ़ कीजिए, मैं इसमें मदद नहीं कर सकता।" if s.lang == "hi" else "Sorry, I can't help with that.")
            if response.stop_reason == "pause_turn":
                continue

            tool_uses = [b for b in response.content if b.type == "tool_use"]
            if not tool_uses:
                return " ".join(b.text for b in response.content if b.type == "text").strip()

            results = []
            for tu in tool_uses:
                try:
                    out = self._run_tool(s, tu.name, tu.input or {})
                    results.append({"type": "tool_result", "tool_use_id": tu.id,
                                    "content": json.dumps(out, ensure_ascii=False, default=str)})
                except Exception as e:  # report tool failures to the model instead of crashing the turn
                    log.exception("tool %s failed", tu.name)
                    results.append({"type": "tool_result", "tool_use_id": tu.id,
                                    "content": f"Error: {e}", "is_error": True})
            s.messages.append({"role": "user", "content": results})

        return "Sorry, that took too long. Could you say it again?"
