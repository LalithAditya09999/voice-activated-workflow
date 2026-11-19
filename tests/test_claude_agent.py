"""Exercises the Claude agent's tool loop with a scripted fake client (no network)."""
from pathlib import Path
from types import SimpleNamespace as NS

from app.core.actions import Actions, Session
from app.core.claude_agent import TOOLS, ClaudeAgent
from app.core.domains import load_registry
from app.core.tracker import Tracker

ROOT = Path(__file__).resolve().parent.parent


def tool_use(id_, name, input_):
    return NS(type="tool_use", id=id_, name=name, input=input_)


def text(t):
    return NS(type="text", text=t)


class FakeMessages:
    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        content, stop = self.script.pop(0)
        return NS(content=content, stop_reason=stop)


class FakeClient:
    def __init__(self, script):
        self.beta = NS(messages=FakeMessages(script))


def make(script, tmp_path):
    reg = load_registry(ROOT / "domains", ["farmer", "citizen"])
    actions = Actions(reg, Tracker(tmp_path / "c.db"))
    client = FakeClient(script)
    return ClaudeAgent(actions, "claude-opus-5-5", client=client), client


def test_tool_loop_fills_form_and_requests_confirmation(tmp_path):
    agent, client = make([
        ([tool_use("t1", "start_form", {"form_id": "solar_pump_kusum"})], "tool_use"),
        ([tool_use("t2", "set_form_fields", {"values": {
            "name": "Murugan", "phone": "9876543210", "aadhaar": "123456789012", "district": "Erode",
            "taluk": "Bhavani", "village": "Ammapettai", "survey_number": "45/2", "land_acres": 3,
            "water_source": "borewell", "has_grid_connection": False, "pump_hp": 5}})], "tool_use"),
        ([tool_use("t3", "request_confirmation", {})], "tool_use"),
        ([text("பெயர் முருகன், ... எல்லாம் சரியா?")], "end_turn"),
        ([tool_use("t4", "submit_form", {"user_confirmed": True})], "tool_use"),
        ([text("முடிந்தது! குறிப்பு எண் ...")], "end_turn"),
    ], tmp_path)
    s = Session(lang="ta")
    reply = agent.respond(s, "எனக்கு 5 HP சோலார் பம்ப் வேணும், நான் முருகன், ஈரோடு...")
    assert "சரியா" in reply and s.form.awaiting_confirmation
    assert s.form.values["aadhaar"] == "XXXX-XXXX-9012"

    reply = agent.respond(s, "ஆமாம் சரி")
    assert s.form is None
    assert any(e["type"] == "application" for e in s.events)

    # request shape: tools, effort, fallbacks, and alternating roles with tool results
    call = client.beta.messages.calls[0]
    assert call["model"] == "claude-opus-5-5" and call["tools"] is TOOLS
    assert call["fallbacks"] == "default" and call["output_config"] == {"effort": "low"}
    roles = [m["role"] for m in s.messages]
    assert all(a != b for a, b in zip(roles, roles[1:])), roles


def test_validation_errors_go_back_to_model(tmp_path):
    agent, client = make([
        ([tool_use("t1", "start_form", {"form_id": "grievance"})], "tool_use"),
        ([tool_use("t2", "set_form_fields", {"values": {"phone": "123"}})], "tool_use"),
        ([text("Mobile number should have 10 digits. Could you say it again?")], "end_turn"),
    ], tmp_path)
    s = Session(lang="en")
    agent.respond(s, "complaint, my number is 123")
    last_results = s.messages[-2]["content"]
    assert "10 digits" in last_results[0]["content"]


def test_submit_without_readback_is_refused(tmp_path):
    agent, _ = make([
        ([tool_use("t1", "start_form", {"form_id": "grievance"})], "tool_use"),
        ([tool_use("t2", "set_form_fields", {"values": {
            "department": "water", "description": "No water for a week in our street",
            "since_when": "a week", "name": "Selvi", "phone": "9876543210", "district": "Madurai", "village": "Melur"}})], "tool_use"),
        ([tool_use("t3", "submit_form", {"user_confirmed": True})], "tool_use"),
        ([text("Let me read it back first.")], "end_turn"),
    ], tmp_path)
    s = Session(lang="en")
    agent.respond(s, "file a complaint")
    assert s.form is not None  # still open: the engine refused to submit without a read-back
    assert "read the details back" in s.messages[-2]["content"][0]["content"]


def test_refusal_returns_polite_message(tmp_path):
    agent, _ = make([([], "refusal")], tmp_path)
    s = Session(lang="en")
    assert "can't help" in agent.respond(s, "something")
