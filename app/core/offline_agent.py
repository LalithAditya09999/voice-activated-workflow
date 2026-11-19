"""Rule-based agent: works with no API key and no internet.

It's deliberately simple (keyword routing + form filling one field at a time), but it
exercises the same Actions as the Claude agent, so the demo never dies on bad Wi-Fi.
"""
from __future__ import annotations

from .actions import Actions, Session
from .forms import t
from .text import is_cancel, is_no, is_yes, tokens

S = {
    "greeting": {
        "en": "Hello! I'm Velan, your helper. Tell me what you need — a subsidy, insurance, a certificate, or farming advice.",
        "ta": "வணக்கம்! நான் வேலன், உங்கள் உதவியாளர். உங்களுக்கு என்ன வேண்டும் என்று சொல்லுங்கள் — மானியம், காப்பீடு, சான்றிதழ், அல்லது விவசாய ஆலோசனை.",
        "hi": "नमस्ते! मैं वेलन हूँ, आपका सहायक। बताइए आपको क्या चाहिए — सब्सिडी, बीमा, प्रमाणपत्र, या खेती की सलाह।",
    },
    "offer_form": {
        "en": "Shall I fill the application with you now? It takes about {n} questions.",
        "ta": "இப்போதே விண்ணப்பத்தை உங்களுடன் நிரப்பலாமா? சுமார் {n} கேள்விகள்.",
        "hi": "क्या मैं अभी आपके साथ आवेदन भरूँ? लगभग {n} सवाल होंगे।",
    },
    "documents": {"en": "Documents needed: {docs}.", "ta": "தேவையான ஆவணங்கள்: {docs}.", "hi": "ज़रूरी दस्तावेज़: {docs}।"},
    "starting": {"en": "Let's start: {title}.", "ta": "தொடங்கலாம்: {title}.", "hi": "शुरू करते हैं: {title}।"},
    "readback": {
        "en": "Let me read it back. {items}. Is everything correct?",
        "ta": "சரிபார்க்கிறேன். {items}. எல்லாம் சரியா?",
        "hi": "मैं पढ़कर सुनाता हूँ। {items}। क्या सब सही है?",
    },
    "which_wrong": {
        "en": "Which detail should I change? Say its name, like 'phone' or 'village'.",
        "ta": "எந்த விவரத்தை மாற்ற வேண்டும்? அதன் பெயரைச் சொல்லுங்கள், உதா. 'மொபைல்' அல்லது 'கிராமம்'.",
        "hi": "कौन सी जानकारी बदलनी है? उसका नाम बताइए, जैसे 'मोबाइल' या 'गाँव'।",
    },
    "submitted": {
        "en": "Done! Your reference number is {id}. Take the printed form and documents to {to}. I'll remind you to follow up on {date}.",
        "ta": "முடிந்தது! உங்கள் குறிப்பு எண் {id}. அச்சிட்ட படிவத்தையும் ஆவணங்களையும் {to} கொண்டு செல்லுங்கள். {date} அன்று நினைவூட்டுகிறேன்.",
        "hi": "हो गया! आपका संदर्भ नंबर {id} है। छपा हुआ फ़ॉर्म और दस्तावेज़ {to} ले जाइए। मैं {date} को याद दिलाऊँगा।",
    },
    "cancelled": {"en": "Okay, I've stopped. What else can I help with?", "ta": "சரி, நிறுத்திவிட்டேன். வேறு என்ன உதவி வேண்டும்?", "hi": "ठीक है, रोक दिया। और क्या मदद करूँ?"},
    "not_found": {
        "en": "I'm not sure about that yet. You can ask about drip irrigation, solar pumps, PM-KISAN, crop insurance, seeds, or certificates. Please also confirm at your nearest agriculture office.",
        "ta": "இது பற்றி எனக்கு உறுதியாகத் தெரியவில்லை. சொட்டு நீர் பாசனம், சூரிய பம்ப், பிஎம்-கிசான், பயிர் காப்பீடு, விதைகள், சான்றிதழ்கள் பற்றிக் கேட்கலாம். அருகிலுள்ள வேளாண் அலுவலகத்திலும் உறுதி செய்யுங்கள்.",
        "hi": "इसके बारे में मुझे पक्का नहीं पता। आप ड्रिप सिंचाई, सोलर पंप, पीएम-किसान, फसल बीमा, बीज या प्रमाणपत्र के बारे में पूछ सकते हैं। नज़दीकी कृषि कार्यालय में भी पुष्टि करें।",
    },
    "elig_intro": {
        "en": "I'll ask a few quick questions and find every scheme you can claim.",
        "ta": "சில கேள்விகள் கேட்டு, நீங்கள் பெறக்கூடிய எல்லாத் திட்டங்களையும் கண்டுபிடிக்கிறேன்.",
        "hi": "मैं कुछ छोटे सवाल पूछकर वो सारी योजनाएँ ढूँढूँगा जिनका आप लाभ ले सकते हैं।",
    },
    "elig_result": {
        "en": "You are likely eligible for: {yes}.", "ta": "நீங்கள் பெறக்கூடியவை: {yes}.", "hi": "आप इनके लिए पात्र हो सकते हैं: {yes}।",
    },
    "elig_maybe": {
        "en": "Need more details for: {maybe}.", "ta": "மேலும் விவரம் தேவை: {maybe}.", "hi": "इनके लिए और जानकारी चाहिए: {maybe}।",
    },
    "elig_none": {
        "en": "I couldn't find a scheme that fits yet.", "ta": "பொருந்தும் திட்டம் இன்னும் கிடைக்கவில்லை.", "hi": "अभी कोई उपयुक्त योजना नहीं मिली।",
    },
    "elig_next": {
        "en": "Say the scheme name to start its application.", "ta": "விண்ணப்பிக்க திட்டத்தின் பெயரைச் சொல்லுங்கள்.", "hi": "आवेदन शुरू करने के लिए योजना का नाम बोलिए।",
    },
    "also": {"en": "I can also explain: {topics}.", "ta": "இவற்றையும் விளக்க முடியும்: {topics}.", "hi": "मैं ये भी बता सकता हूँ: {topics}।"},
    "apps": {"en": "Your applications: {list}.", "ta": "உங்கள் விண்ணப்பங்கள்: {list}.", "hi": "आपके आवेदन: {list}।"},
    "no_apps": {"en": "You have no applications yet.", "ta": "இன்னும் விண்ணப்பம் எதுவும் இல்லை.", "hi": "अभी कोई आवेदन नहीं है।"},
    "verify": {
        "en": "(Please verify current rules at the office.)", "ta": "(தற்போதைய விதிகளை அலுவலகத்தில் உறுதி செய்யுங்கள்.)", "hi": "(मौजूदा नियम कार्यालय में ज़रूर जाँचें।)",
    },
}

ELIGIBILITY_WORDS = {
    "eligible", "eligibility", "schemes", "scheme", "benefits", "benefit", "entitled", "claim",
    "yojana", "yojna", "योजना", "योजनाएं", "योजनाएँ", "पात्र", "लाभ",
    "திட்டம்", "திட்டங்கள்", "தகுதி", "பலன்", "சலுகை",
}
TRACK_WORDS = {
    "status", "track", "application", "applications", "reference",
    "स्थिति", "आवेदन", "ஸ்டேட்டஸ்", "நிலை", "விண்ணப்பம்", "விண்ணப்பங்கள்",
}
SEP = {"en": "; ", "ta": "; ", "hi": "; "}


def s_(key: str, lang: str, **kw) -> str:
    return t(S[key], lang).format(**kw)


class OfflineAgent:
    name = "offline"

    def __init__(self, actions: Actions):
        self.a = actions

    def respond(self, s: Session, text: str) -> str:
        lang = s.lang
        if not text.strip():
            return s_("greeting", lang)

        if s.form:
            return self._continue_form(s, text)

        # yes/no to a pending "shall I fill the form?"
        if s.pending_service:
            svc = self.a.reg.services[s.pending_service]
            if is_yes(text):
                return self._begin_form(s, svc.form)
            if is_no(text):
                s.pending_service = None
                return s_("cancelled", lang)
            s.pending_service = None  # they moved on; treat as a new request

        toks = set(tokens(text))
        if toks & TRACK_WORDS and not self.a.reg.match_service(text):
            return self._applications(s)

        svc = self.a.reg.match_service(text)
        if svc and not svc.form:
            return self._advise(s, svc, text)
        if svc:
            return self._explain(s, svc.id)

        if toks & ELIGIBILITY_WORDS:
            s.pending_service = None
            self.a.start_form(s, "eligibility_profile")
            return s_("elig_intro", lang) + " " + self._ask_next(s)

        hits = self.a.search_knowledge(s, text, k=1)["results"]
        if hits:
            h = hits[0]
            answer = h["summary"] or h["content"][:400]
            return f"{h['title']}: {answer} {s_('verify', lang) if not h['verified'] else ''}".strip()
        return s_("not_found", lang)

    # ---------------------------------------------------------------
    def _explain(self, s: Session, service_id: str) -> str:
        info = self.a.explain_service(s, service_id)
        parts = [info["title"] + "."]
        parts += info["summary"]
        if info["documents"]:
            parts.append(s_("documents", s.lang, docs=", ".join(info["documents"])))
        if info["form_id"]:
            n = len([f for f in self.a.reg.forms[info["form_id"]]["fields"] if not f.get("ask_if")])
            parts.append(s_("offer_form", s.lang, n=n))
            s.pending_service = service_id
        return " ".join(p for p in parts if p)

    def _advise(self, s: Session, svc, text: str) -> str:
        """Knowledge-only service: answer with the article that best fits the question."""
        ranked = {d.id: score for d, score in self.a.reg.search(text, k=len(self.a.reg.knowledge))}
        docs = sorted((self.a.reg.knowledge[k] for k in svc.knowledge), key=lambda d: -ranked.get(d.id, 0))
        best, others = docs[0], docs[1:]
        s.emit("sources", [{"id": best.id, "title": best.title, "source": best.source, "verified": best.verified}])
        answer = t(best.summary, s.lang) if best.summary else best.body[:400]
        out = f"{answer} {s_('verify', s.lang) if not best.verified else ''}".strip()
        if others:
            out += " " + s_("also", s.lang, topics=", ".join(d.title for d in others))
        return out

    def _begin_form(self, s: Session, form_id: str) -> str:
        self.a.start_form(s, form_id)
        return s_("starting", s.lang, title=t(s.form.form["title"], s.lang)) + " " + self._ask_next(s)

    def _ask_next(self, s: Session) -> str:
        nxt = s.form.next_field()
        if nxt:
            return s.form.question(nxt, s.lang)
        self.a.request_confirmation(s)
        items = SEP[s.lang if s.lang in SEP else "en"].join(f"{k}: {v}" for k, v in s.form.readback(s.lang))
        return s_("readback", s.lang, items=items)

    def _continue_form(self, s: Session, text: str) -> str:
        lang = s.lang
        if is_cancel(text):
            self.a.cancel_form(s)
            return s_("cancelled", lang)

        if s.form.awaiting_confirmation:
            if is_yes(text):
                is_profile = s.form.form.get("kind") == "profile"
                res = self.a.submit_form(s, user_confirmed=True)
                if is_profile:
                    return self._eligibility_summary(res["results"], lang)
                return s_("submitted", lang, id=res["id"], to=res["submit_to"], date=res["follow_up_on"])
            f = s.form.find_field_mentioned(text, lang)
            if f:
                return self.a.edit_field(s, f["id"])["ask"]
            return s_("which_wrong", lang)

        nxt = s.form.next_field()
        res = self.a.set_form_fields(s, {nxt["id"]: text})
        if res["errors"]:
            return f"{next(iter(res['errors'].values()))} {s.form.question(nxt, lang)}"
        return self._ask_next(s)

    def _eligibility_summary(self, results: list[dict], lang: str) -> str:
        yes = [r["name"] for r in results if r["status"] == "eligible"]
        maybe = [r["name"] for r in results if r["status"] == "maybe"]
        out = []
        out.append(s_("elig_result", lang, yes=", ".join(yes)) if yes else s_("elig_none", lang))
        if maybe:
            out.append(s_("elig_maybe", lang, maybe=", ".join(maybe)))
        if yes:
            out.append(s_("elig_next", lang))
        return " ".join(out)

    def _applications(self, s: Session) -> str:
        apps = self.a.list_applications(s)["applications"]
        if not apps:
            return s_("no_apps", s.lang)
        listing = SEP["en"].join(f"{a['title']} ({a['id']}, {a['status']})" for a in apps[:5])
        return s_("apps", s.lang, list=listing)
