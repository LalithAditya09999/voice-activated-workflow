import json
import sys
from pathlib import Path

from app.core.actions import Actions, Session
from app.core.domains import load_registry
from app.core.offline_agent import OfflineAgent
from app.core.tracker import Tracker

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ingest  # noqa: E402


def test_subtitles_are_cleaned_and_chunked(tmp_path):
    vtt = tmp_path / "talk.vtt"
    vtt.write_text("WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nமண்ணுக்கு உணவிடு.\n\n"
                   "00:00:03.000 --> 00:00:05.000\nமண்ணுக்கு உணவிடு.\n\n00:00:05.000 --> 00:00:07.000\n<c>செடிக்கு அல்ல.</c>\n",
                   encoding="utf-8")
    text = ingest.read_source(vtt)
    assert text == "மண்ணுக்கு உணவிடு. செடிக்கு அல்ல."
    assert len(ingest.chunk("a. " * 2000, size=500)) > 1


def test_source_without_permission_is_refused():
    errs = ingest.validate({"id": "x", "title": "t", "author": "a", "files": [], "permission": {"granted_by": ""}})
    assert any("permission.granted_by" in e for e in errs) and any("permission.date" in e for e in errs)


def test_ingest_writes_attributed_articles(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest, "ROOT", tmp_path)
    (tmp_path / "domains/farmer/knowledge").mkdir(parents=True)
    (tmp_path / "raw.txt").write_text("Keep the soil covered.\n\nGrow many crops together.", encoding="utf-8")
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps([{
        "id": "talk1", "title": "Talk", "author": "G. Nammalvar", "files": ["raw.txt"],
        "permission": {"granted_by": "Vanagam", "date": "2026-11-25", "scope": "app use"}}]), encoding="utf-8")
    assert ingest.ingest(manifest, dry_run=False, do_summary=False) == 0
    out = (tmp_path / "domains/farmer/knowledge/src_talk1_1.md").read_text(encoding="utf-8")
    assert "Used with permission of Vanagam" in out and '"verified": false' in out


def test_compare_answer_gives_both_sides(tmp_path):
    reg = load_registry(ROOT / "domains", ["farmer", "citizen"])
    agent = OfflineAgent(Actions(reg, Tracker(tmp_path / "t.db")))
    s = Session(lang="en")
    reply = agent.respond(s, "Chemical fertiliser or organic — which is better for my paddy?")
    assert "Common practice" in reply and "Organic practice" in reply
    assert "fertilisers" in reply  # the nutrition comparison, not the pesticide one
    s = Session(lang="ta")
    reply = agent.respond(s, "என் நெல்லுக்கு ரசாயன உரமா இயற்கை உரமா, எது நல்லது?")
    assert "யூரியா" in reply
    s = Session(lang="ta")
    reply = agent.respond(s, "நம்மாழ்வார் அமிர்தக் கரைசல் எப்படி தயாரிப்பது?")
    assert "அமிர்தக் கரைசல்" in reply


def test_every_compare_doc_has_both_sections():
    reg = load_registry(ROOT / "domains", ["farmer"])
    compare = [d for d in reg.knowledge.values() if d.id.startswith("compare_") or d.id == "poultry_country_chicken"]
    assert len(compare) >= 4
    for d in compare:
        assert {"en", "ta", "hi"} <= set(d.summary)
        assert "side effects" in d.body.lower() or "risks" in d.body.lower(), d.id
