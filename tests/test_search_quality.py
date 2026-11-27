"""Guards search quality on 48 realistic questions (clear and hard: misspellings,
romanised Tamil/Hindi, joined words). Run `python -m pytest tests/test_search_quality.py -q -s`
to see the scores."""
import json
from pathlib import Path

from app.core.domains import load_registry

ROOT = Path(__file__).resolve().parent.parent
EVAL = json.loads((ROOT / "tests" / "search_eval.json").read_text(encoding="utf-8"))


def score(fn, subset):
    return sum(fn(e["q"])[:1] == [e["expect"]] for e in subset)


def test_hybrid_beats_or_matches_keyword_search():
    reg = load_registry(ROOT / "domains", ["farmer", "citizen"])
    hybrid = lambda q: [d.id for d, _ in reg.search(q, 3)]
    keyword = lambda q: [d.id for d, _ in reg.keyword_search(q, 3)]
    for name in ("clear", "hard"):
        subset = [e for e in EVAL if e["set"] == name]
        h, k = score(hybrid, subset), score(keyword, subset)
        print(f"{name}: hybrid {h}/{len(subset)}  keyword {k}/{len(subset)}")
        assert h >= k
    clear = [e for e in EVAL if e["set"] == "clear"]
    hard = [e for e in EVAL if e["set"] == "hard"]
    assert score(hybrid, clear) >= 33 and score(hybrid, hard) >= 14
