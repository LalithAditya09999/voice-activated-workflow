from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_config_and_static():
    cfg = client.get("/api/config").json()
    assert cfg["agent"] == "offline" and set(cfg["languages"]) == {"ta", "hi", "en"}
    assert client.get("/").status_code == 200
    assert client.get("/app.js").status_code == 200


def test_chat_roundtrip_and_print():
    sid = client.post("/api/session", json={"lang": "en"}).json()["session_id"]
    r = client.post("/api/chat", json={"session_id": sid, "text": "I want to file a complaint"}).json()
    assert "Shall I fill" in r["reply"]
    r = client.post("/api/chat", json={"session_id": sid, "text": "yes"}).json()
    assert r["form"]["form_id"] == "grievance"
    for text in ["water", "No drinking water supply in our street", "two weeks", "Selvi", "9876543210", "yes", "Madurai", "Melur"]:
        r = client.post("/api/chat", json={"session_id": sid, "text": text}).json()
    assert r["form"]["awaiting_confirmation"]
    r = client.post("/api/chat", json={"session_id": sid, "text": "yes"}).json()
    app_ev = [e for e in r["events"] if e["type"] == "application"][0]["data"]
    page = client.get(app_ev["print_url"])
    assert page.status_code == 200 and "Selvi" in page.text and app_ev["id"] in page.text


def test_unknown_session_404():
    assert client.post("/api/chat", json={"session_id": "nope", "text": "hi"}).status_code == 404


def test_server_speech_disabled_without_key():
    assert client.post("/api/tts", json={"text": "hi", "lang": "ta"}).status_code == 501
