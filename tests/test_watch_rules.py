import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import watch_rules as w  # noqa: E402


def setup(tmp_path, monkeypatch):
    shutil.copytree(ROOT / "domains", tmp_path / "domains")
    monkeypatch.setattr(w, "DOMAINS", tmp_path / "domains")
    monkeypatch.setattr(w, "STATE_DIR", tmp_path / "watch")


def test_page_text_strips_markup():
    raw = "<html><head><title>x</title></head><body><script>var a=1</script><p>Subsidy: 75%</p><div>Apply by 31 Dec</div></body></html>"
    assert w.page_text(raw) == "Subsidy: 75%\nApply by 31 Dec"


def test_change_is_queued_then_approved(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    pages = {}
    fetcher = lambda url: pages.get(url, "<p>Instalment: Rs 2000</p><p>e-KYC is mandatory</p>")
    summarizer = lambda title, body, diff: {"relevant": True, "summary": "Instalment raised to Rs 3000.",
                                            "changes": [], "suggested_update": ""}
    first = w.check(fetcher, summarizer)
    assert first["baseline"] == first["checked"] and first["changed"] == 0
    assert w.check(fetcher, summarizer)["unchanged"] == first["checked"]

    pages["https://pmkisan.gov.in/"] = "<p>Instalment: Rs 3000</p><p>e-KYC is mandatory</p>"
    third = w.check(fetcher, summarizer)
    assert third["changed"] == 1
    [item] = w.pending()
    assert item["doc_id"] == "pm_kisan" and "-Instalment: Rs 2000" in item["diff"] and "+Instalment: Rs 3000" in item["diff"]

    w.approve(item["id"], by="Agri officer")
    text = (tmp_path / "domains/farmer/knowledge/pm_kisan.md").read_text(encoding="utf-8")
    assert "## Rule updates" in text and "Instalment raised to Rs 3000." in text and "Reviewed by Agri officer" in text
    assert '"last_checked"' in text and w.pending() == []


def test_failed_fetch_does_not_stop_the_run(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    def fetcher(url):
        if "pmfby" in url:
            raise ConnectionError("blocked")
        return "<p>ok</p>"
    counts = w.check(fetcher, lambda *a: None)
    assert counts["failed"] == 1 and counts["checked"] >= 1


def test_every_source_points_to_an_existing_article():
    for pack, doc_id, src in w.all_sources():
        assert (ROOT / "domains" / pack / "knowledge" / f"{doc_id}.md").exists(), doc_id
        assert src["url"].startswith("https://")
