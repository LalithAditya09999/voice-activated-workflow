"""Domain packs: everything problem-specific lives in domains/<pack>/ as data.

A pack folder contains:
  domain.json        name + list of services (keywords, linked form + knowledge)
  forms/*.json       form schemas (fields may reference shared fields via "$ref")
  knowledge/*.md     knowledge articles with a small front-matter header
  schemes.json       (optional) eligibility rules evaluated against a profile

Swapping or adding a pack is how the app adapts to a new problem statement.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .semantic import CharNgramIndex
from .text import normalize, tokens

# trailing Tamil / Devanagari vowel signs and virama: உரம் / உரமா / உரமும் share the stem உரம
_INDIC_SIGNS = set(chr(c) for c in [*range(0x0BBE, 0x0BCE), *range(0x093E, 0x094E), 0x0902, 0x0903])


def stem(tok: str) -> str:
    if tok.isascii():
        return tok
    while len(tok) > 2 and tok[-1] in _INDIC_SIGNS:
        tok = tok[:-1]
    return tok


def search_tokens(text: str) -> list[str]:
    return [stem(t) for t in tokens(text)]


@dataclass
class KnowledgeDoc:
    id: str
    domain: str
    title: str
    tags: list[str]
    summary: dict[str, str]
    body: str
    source: str = ""
    verified: bool = False

    last_checked: str = ""

    def text_for_search(self) -> str:
        return " ".join([self.title, " ".join(self.tags), " ".join(self.summary.values()), self.body])

    def text_for_ml(self) -> str:
        # title and tags weigh more: they are what people ask about
        return " ".join([self.title] * 3 + self.tags * 2 + list(self.summary.values()) + [self.body])


@dataclass
class Service:
    id: str
    domain: str
    title: dict[str, str]
    keywords: list[str]
    form: str | None
    knowledge: list[str]


@dataclass
class Registry:
    domains: dict[str, dict] = field(default_factory=dict)
    services: dict[str, Service] = field(default_factory=dict)
    forms: dict[str, dict] = field(default_factory=dict)
    knowledge: dict[str, KnowledgeDoc] = field(default_factory=dict)
    schemes: list[dict] = field(default_factory=list)
    _idf: dict[str, float] = field(default_factory=dict)
    _doc_tf: dict[str, Counter] = field(default_factory=dict)
    _ml: CharNgramIndex | None = None

    # ---------- knowledge search (BM25-lite, works across scripts) ----------
    def _index(self) -> None:
        df: Counter = Counter()
        for doc in self.knowledge.values():
            tf = Counter(search_tokens(doc.text_for_search()))
            # tags and title count extra
            for t in search_tokens(doc.title + " " + " ".join(doc.tags)):
                tf[t] += 3
            self._doc_tf[doc.id] = tf
            df.update(set(tf))
        n = max(len(self.knowledge), 1)
        self._idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self._ml = CharNgramIndex().fit({d.id: d.text_for_ml() for d in self.knowledge.values()})

    def search(self, query: str, k: int = 3) -> list[tuple[KnowledgeDoc, float]]:
        """Hybrid retrieval: keyword (BM25-style) + character n-gram ML, each scaled to its best
        hit and averaged. Keyword wins on exact terms; the ML half catches misspellings,
        romanised Tamil/Hindi, joined words and inflections. See tests/search_eval.json."""
        kw = {d.id: s for d, s in self.keyword_search(query, k=len(self.knowledge))}
        ml = self._ml.query(query) if self._ml else {}
        top_kw, top_ml = max(kw.values(), default=0) or 1, max(ml.values(), default=0) or 1
        scores = {i: 0.5 * kw.get(i, 0) / top_kw + 0.5 * ml.get(i, 0) / top_ml for i in set(kw) | set(ml)}
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(self.knowledge[i], sc) for i, sc in ranked[:k] if sc > 0.05]

    def keyword_search(self, query: str, k: int = 3) -> list[tuple[KnowledgeDoc, float]]:
        q = [t for t in search_tokens(query) if len(t) > 1]
        scored = []
        for doc_id, tf in self._doc_tf.items():
            length = sum(tf.values()) or 1
            score = 0.0
            for t in q:
                # prefix match lets "subsidies" hit "subsidy" and Tamil suffixed forms hit stems
                hits = tf.get(t, 0)
                if not hits and len(t) >= 4:
                    prefix = t[:5]
                    hits = 0.5 * sum(c for w, c in tf.items() if w.startswith(prefix))
                if hits:
                    idf = self._idf.get(t, max(self._idf.values(), default=1.0) / 2)
                    score += idf * (hits * 2.2) / (hits + 1.2 * (0.25 + 0.75 * length / 400))
            if score > 0:
                scored.append((self.knowledge[doc_id], score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def match_service(self, text: str) -> Service | None:
        low = normalize(text).lower()
        toks = set(tokens(text))
        best, best_score = None, 0
        for svc in self.services.values():
            score = 0
            for kw in svc.keywords:
                kw_l = kw.lower()
                # Tamil nouns ending in a virama (சேதம்) inflect by replacing it (சேதமானது, சேதமாக):
                # dropping the final virama lets the stem match the inflected forms.
                if kw_l.endswith("்") and len(kw_l) > 3:
                    kw_l = kw_l[:-1]
                if " " in kw_l or not kw_l.isascii():
                    score += 2 * (kw_l in low)
                else:
                    score += 2 * (kw_l in toks) + (any(t.startswith(kw_l) for t in toks) and kw_l not in toks)
            if score > best_score:
                best, best_score = svc, score
        return best if best_score >= 2 else None


_FRONT_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def _parse_md(path: Path, domain: str) -> KnowledgeDoc:
    raw = path.read_text(encoding="utf-8")
    m = _FRONT_RE.match(raw)
    meta: dict = {}
    body = raw
    if m:
        meta = json.loads(m.group(1))
        body = m.group(2).strip()
    return KnowledgeDoc(
        id=meta.get("id", path.stem),
        domain=domain,
        title=meta.get("title", path.stem),
        tags=meta.get("tags", []),
        summary=meta.get("summary", {}),
        body=body,
        source=meta.get("source", ""),
        verified=bool(meta.get("verified", False)),
        last_checked=meta.get("last_checked", ""),
    )


def _resolve_fields(form: dict, common: dict) -> dict:
    resolved = []
    for f in form.get("fields", []):
        if "$ref" in f:
            base = dict(common[f["$ref"]])
            base.update({k: v for k, v in f.items() if k != "$ref"})
            base.setdefault("id", f["$ref"])
            f = base
        resolved.append(f)
    form["fields"] = resolved
    return form


def load_registry(domains_dir: Path, enabled: list[str]) -> Registry:
    reg = Registry()
    common_path = domains_dir / "_common" / "fields.json"
    common = json.loads(common_path.read_text(encoding="utf-8")) if common_path.exists() else {}
    # shared forms (e.g. the eligibility profile) are available whichever packs are enabled
    for fp in sorted((domains_dir / "_common" / "forms").glob("*.json")):
        form = json.loads(fp.read_text(encoding="utf-8"))
        form["domain"] = "_common"
        reg.forms[form["id"]] = _resolve_fields(form, common)

    for name in enabled:
        pack = domains_dir / name
        if not pack.is_dir():
            raise FileNotFoundError(f"Domain pack not found: {pack}")
        meta = json.loads((pack / "domain.json").read_text(encoding="utf-8"))
        reg.domains[name] = meta
        for svc in meta.get("services", []):
            reg.services[svc["id"]] = Service(
                id=svc["id"], domain=name, title=svc["title"], keywords=svc.get("keywords", []),
                form=svc.get("form"), knowledge=svc.get("knowledge", []),
            )
        for fp in sorted((pack / "forms").glob("*.json")):
            form = json.loads(fp.read_text(encoding="utf-8"))
            form["domain"] = name
            reg.forms[form["id"]] = _resolve_fields(form, common)
        for kp in sorted((pack / "knowledge").glob("*.md")):
            doc = _parse_md(kp, name)
            reg.knowledge[doc.id] = doc
        schemes = pack / "schemes.json"
        if schemes.exists():
            for s in json.loads(schemes.read_text(encoding="utf-8")):
                s["domain"] = name
                reg.schemes.append(s)

    # validate cross references early so a bad pack fails at startup, not mid-call
    for svc in reg.services.values():
        if svc.form and svc.form not in reg.forms:
            raise ValueError(f"Service {svc.id} references missing form {svc.form}")
        for k in svc.knowledge:
            if k not in reg.knowledge:
                raise ValueError(f"Service {svc.id} references missing knowledge doc {k}")
    reg._index()
    return reg
