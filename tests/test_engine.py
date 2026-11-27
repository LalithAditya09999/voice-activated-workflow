from datetime import date, timedelta
from pathlib import Path

import pytest

from app.core.actions import Actions, Session
from app.core.domains import load_registry
from app.core.eligibility import evaluate
from app.core.forms import FieldError, coerce
from app.core.offline_agent import OfflineAgent
from app.core.tracker import Tracker

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def reg():
    return load_registry(ROOT / "domains", ["farmer", "citizen"])


@pytest.fixture
def agent(reg, tmp_path):
    return OfflineAgent(Actions(reg, Tracker(tmp_path / "t.db")))


def test_registry_loads_every_pack(reg):
    assert "drip_irrigation" in reg.forms and "income_certificate" in reg.forms
    assert "eligibility_profile" in reg.forms
    # every form field resolved from $ref has a question in all three languages
    for form in reg.forms.values():
        for f in form["fields"]:
            assert {"en", "ta", "hi"} <= set(f["question"]), (form["id"], f["id"])


@pytest.mark.parametrize("text,service", [
    ("I want drip irrigation", "drip_irrigation"),
    ("எனக்கு சொட்டு நீர் பாசனம் வேண்டும்", "drip_irrigation"),
    ("मुझे सोलर पंप चाहिए", "solar_pump"),
    ("நேற்று மழையில் என் நெல் சேதமானது", "crop_insurance"),
    ("Kisan Credit Card", "kcc"),
    ("கிசான் கடன் அட்டை", "kcc"),
    ("முதியோர் ஓய்வூதியம்", "old_age_pension"),
    ("jeevamirtham kaise banaye", "organic_inputs"),
])
def test_service_matching(reg, text, service):
    assert reg.match_service(text).id == service


def test_knowledge_search_tamil(reg):
    assert reg.search("சம்பா பருவம்")[0][0].id == "tn_cropping_seasons"


@pytest.mark.parametrize("ftype,raw,expected", [
    ({"type": "phone"}, "98765 43210", "9876543210"),
    ({"type": "phone"}, "+91 98765 43210", "9876543210"),
    ({"type": "phone"}, "௯௮௭௬௫௪௩௨௧௦", "9876543210"),  # Tamil digits
    ({"type": "aadhaar"}, "1234 5678 9012", "XXXX-XXXX-9012"),
    ({"type": "number", "min": 0, "max": 50}, "இரண்டரை ஏக்கர் 2.5", 2.5),
    ({"type": "number"}, "ரெண்டு", 2),
    ({"type": "yesno"}, "ஆமாம்", True),
    ({"type": "yesno"}, "नहीं", False),
])
def test_coerce(ftype, raw, expected):
    assert coerce(ftype, raw) == expected


def test_coerce_rejects_bad_phone_and_future_date():
    with pytest.raises(FieldError):
        coerce({"type": "phone"}, "12345")
    tomorrow = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y")
    with pytest.raises(FieldError):
        coerce({"type": "date", "past_only": True}, tomorrow)
    assert coerce({"type": "date"}, "நேற்று") == (date.today() - timedelta(days=1)).isoformat()


def test_choice_by_tamil_alias(reg):
    f = next(x for x in reg.forms["drip_irrigation"]["fields"] if x["id"] == "water_source")
    assert coerce(f, "போர்வெல் இருக்கு", "ta") == "borewell"
    assert coerce(f, "kuan", "hi") == "open_well"


def test_full_drip_application_in_tamil(agent):
    s = Session(lang="ta")
    reply = agent.respond(s, "எனக்கு சொட்டு நீர் பாசனம் வேண்டும்")
    assert "ஆவணங்கள்" in reply and s.pending_service == "drip_irrigation"
    agent.respond(s, "ஆமாம்")
    assert s.form and s.form.id == "drip_irrigation"
    # "ஆமாம்" after the phone, Aadhaar and survey number confirms their digit-by-digit read-back
    answers = ["முருகன்", "ராமசாமி", "98765 43210", "ஆமாம்", "1234 5678 9012", "ஆமாம்", "மதுரை", "மேலூர்",
               "கொட்டாம்பட்டி", "123/4", "ஆமாம்", "2", "போர்வெல்", "தென்னை", "சிறு"]
    reply = ""
    for a in answers:
        reply = agent.respond(s, a)
    assert s.form.awaiting_confirmation and "சரியா" in reply
    assert "XXXX-XXXX-9012" in reply  # Aadhaar is masked in the read-back

    # user corrects the phone number before confirming
    reply = agent.respond(s, "இல்லை, மொபைல் எண் தவறு")
    assert "மொபைல்" in reply
    reply = agent.respond(s, "91234 56789")
    assert "9 1 2 3 4, 5 6 7 8 9" in reply  # read back digit by digit
    reply = agent.respond(s, "சரி")         # digits confirmed -> full read-back again
    assert s.form.awaiting_confirmation and "சரியா" in reply
    reply = agent.respond(s, "சரி")
    assert s.form is None
    app = [e for e in s.events if e["type"] == "application"][0]["data"]
    assert app["id"].startswith("US-")
    stored = agent.a.tracker.get(app["id"])
    assert stored["values"]["phone"] == "9123456789"
    assert stored["values"]["aadhaar"] == "XXXX-XXXX-9012"


def test_invalid_answer_reasks(agent):
    s = Session(lang="en")
    agent.respond(s, "solar pump")
    agent.respond(s, "yes")
    agent.respond(s, "Lakshmi")
    reply = agent.respond(s, "12345")
    assert "10 digits" in reply and s.form.next_field()["id"] == "phone"


def test_digit_confirmation_no_and_repeat(agent):
    s = Session(lang="en")
    agent.respond(s, "solar pump")
    agent.respond(s, "yes")
    agent.respond(s, "Lakshmi")
    reply = agent.respond(s, "98765 43210")
    assert reply == "I heard 9 8 7 6 5, 4 3 2 1 0. Is that right?"
    reply = agent.respond(s, "no")                      # wrong -> asked again
    assert "mobile number" in reply.lower() and "phone" not in s.form.values
    agent.respond(s, "98765 43211")
    reply = agent.respond(s, "no it is 98765 43219")    # repeated number replaces it
    assert "4 3 2 1 9" in reply and s.form.values["phone"] == "9876543219"


def test_noise_is_not_guessed(agent):
    s = Session(lang="ta")
    assert "சரியாகக் கேட்கவில்லை" in agent.respond(s, " ... ?? ")


def test_crop_loss_deadline_first_and_details_reused(agent):
    s = Session(lang="ta")
    reply = agent.respond(s, "நேற்று மழையில் என் நெல் சேதமானது, ரெண்டு ஏக்கர்")
    assert reply.startswith("சேதம் நடந்த 72 மணி நேரத்துக்குள்")   # the deadline is said first
    reply = agent.respond(s, "ஆமாம்")
    v = s.form.values
    assert v["loss_cause"] == "flood" and v["area_affected"] == 2
    assert v["loss_date"] == (date.today() - timedelta(days=1)).isoformat()
    assert "குறித்துக்கொண்டேன்" in reply and "crop" == s.form.next_field()["id"]


def test_cancel(agent):
    s = Session(lang="hi")
    agent.respond(s, "मुझे सोलर पंप चाहिए")
    agent.respond(s, "हाँ")
    agent.respond(s, "रद्द करो")
    assert s.form is None


def test_eligibility_flow(agent):
    s = Session(lang="en")
    agent.respond(s, "Which schemes can I get?")
    assert s.form.id == "eligibility_profile"
    for a in ["yes", "yes", "3", "borewell", "no", "no", "45", "no", "no"]:
        reply = agent.respond(s, a)
    reply = agent.respond(s, "yes")
    assert "PM-KISAN" in reply and "Solar pump" in reply
    results = [e for e in s.events if e["type"] == "eligibility"][0]["data"]
    status = {r["id"]: r["status"] for r in results}
    assert status["pm_kisan"] == "eligible"
    assert status["old_age_pension"] == "not_eligible"


def test_eligibility_rules_reasons(reg):
    res = {r["id"]: r for r in evaluate(reg.schemes, {"is_farmer": True, "owns_land": True, "income_tax_payer": True}, "en")}
    assert res["pm_kisan"]["status"] == "not_eligible"
    assert "income-tax" in res["pm_kisan"]["reasons"][0]
    assert res["pm_kusum"]["status"] == "maybe" and res["pm_kusum"]["missing"] == ["water_source"]


def test_submit_requires_confirmation(reg, tmp_path):
    a = Actions(reg, Tracker(tmp_path / "x.db"))
    s = Session(lang="en")
    a.start_form(s, "grievance")
    a.set_form_fields(s, {"department": "water", "description": "No drinking water in our street for 5 days",
                          "since_when": "5 days", "name": "Selvi", "phone": "9876543210",
                          "district": "Madurai", "village": "Melur"})
    assert "error" in a.submit_form(s, user_confirmed=True)   # not read back yet
    a.request_confirmation(s)
    assert a.submit_form(s, user_confirmed=True)["submitted"]


def test_details_carry_over_between_forms(reg, tmp_path):
    a = Actions(reg, Tracker(tmp_path / "y.db"))
    s = Session(lang="en")
    a.start_form(s, "solar_pump_kusum")
    a.set_form_fields(s, {"name": "Kumar", "phone": "9876543210", "district": "Erode", "village": "Bhavani"})
    a.start_form(s, "farm_power_connection")
    assert s.form.values["name"] == "Kumar" and s.form.values["village"] == "Bhavani"
