"""Turn permitted source material (books, articles, talk transcripts, video subtitles)
into knowledge articles for a domain pack.

    python scripts/ingest.py sources/manifest.json            # write articles
    python scripts/ingest.py sources/manifest.json --dry-run  # just validate
    python scripts/ingest.py sources/manifest.json --summarize  # + short ta/hi/en summaries via Claude

Every source MUST carry a `permission` block (who granted it, when, what scope). Sources
without it are refused — the app only redistributes material its rights holders agreed to.

Supported files: .txt .md (plain text), .srt .vtt (subtitles; timestamps stripped),
.pdf (needs `pip install pypdf`; scanned PDFs need OCR first).
Output: domains/<domain>/knowledge/src_<id>_<n>.md with attribution in the front matter.
Articles are written with "verified": false — review them, then set it to true.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_PERMISSION = ("granted_by", "date", "scope")
CHUNK_CHARS = 1800

_TS = re.compile(r"^\s*(\d+\s*$|\d{1,2}:\d{2}(:\d{2})?[.,]\d{3}\s*-->.*$|WEBVTT.*$|NOTE\b.*$)")


def read_source(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8")
    if suffix in (".srt", ".vtt"):
        lines, last = [], None
        for line in path.read_text(encoding="utf-8").splitlines():
            if _TS.match(line) or not line.strip():
                continue
            line = re.sub(r"<[^>]+>", "", line).strip()
            if line != last:  # auto-captions repeat lines
                lines.append(line)
            last = line
        return " ".join(lines)
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise SystemExit("PDF support needs `pip install pypdf` (or convert the PDF to .txt first)") from e
        return "\n\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    raise ValueError(f"unsupported file type: {path.name}")


def chunk(text: str, size: int = CHUNK_CHARS) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paras) <= 1:  # transcripts have no paragraphs: split on sentence ends
        paras = [p.strip() for p in re.split(r"(?<=[.!?।])\s+", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if cur and len(cur) + len(p) > size:
            chunks.append(cur)
            cur = ""
        cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        chunks.append(cur)
    return chunks


def validate(src: dict) -> list[str]:
    errors = [f"missing '{k}'" for k in ("id", "title", "author", "files") if not src.get(k)]
    perm = src.get("permission") or {}
    errors += [f"permission.{k} is empty" for k in REQUIRED_PERMISSION if not str(perm.get(k, "")).strip()]
    if src.get("id") and not re.fullmatch(r"[a-z0-9_]+", src["id"]):
        errors.append("id must be lowercase letters, digits and _")
    for f in src.get("files", []):
        if not (ROOT / f).exists():
            errors.append(f"file not found: {f}")
    return errors


def summarize(text: str, title: str) -> dict:
    """Short spoken-style summaries in en/ta/hi using Claude (optional)."""
    import anthropic

    client = anthropic.Anthropic()
    schema = {
        "type": "object",
        "properties": {k: {"type": "string"} for k in ("en", "ta", "hi")},
        "required": ["en", "ta", "hi"],
        "additionalProperties": False,
    }
    resp = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=4000,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": (
            f"Source: {title}\n\n{text}\n\n"
            "Summarise the practical farming guidance in this passage in 2-3 short spoken sentences, "
            "faithful to the source (no added facts), once each in English (en), Tamil script (ta) and Hindi (hi).")}],
    )
    if resp.stop_reason == "refusal":
        return {}
    block = next((b for b in resp.content if b.type == "text"), None)
    return json.loads(block.text) if block else {}


def ingest(manifest: Path, dry_run: bool, do_summary: bool) -> int:
    sources = json.loads(manifest.read_text(encoding="utf-8"))
    written, refused = 0, 0
    for src in sources:
        errors = validate(src)
        if errors:
            refused += 1
            print(f"✗ {src.get('id', '?')}: " + "; ".join(errors), file=sys.stderr)
            continue
        text = "\n\n".join(read_source(ROOT / f) for f in src["files"])
        parts = chunk(text)
        domain = src.get("domain", "farmer")
        out_dir = ROOT / "domains" / domain / "knowledge"
        perm = src["permission"]
        attribution = (f"{src['title']} — {src['author']}"
                       + (f" ({src['url']})" if src.get("url") else "")
                       + f". Used with permission of {perm['granted_by']} ({perm['date']}).")
        print(f"✓ {src['id']}: {len(text)} chars → {len(parts)} article(s) in {domain}")
        if dry_run:
            continue
        for i, body in enumerate(parts, 1):
            meta = {
                "id": f"src_{src['id']}_{i}",
                "title": f"{src['title']} (part {i}/{len(parts)})" if len(parts) > 1 else src["title"],
                "approach": src.get("approach", "organic"),
                "tags": src.get("tags", []) + [src["author"]],
                "source": attribution,
                "language": src.get("language", ""),
                "verified": False,
                "summary": summarize(body, src["title"]) if do_summary else {},
            }
            (out_dir / f"{meta['id']}.md").write_text(
                "---\n" + json.dumps(meta, ensure_ascii=False, indent=1) + "\n---\n" + body + "\n", encoding="utf-8")
            written += 1
    print(f"{written} article(s) written, {refused} source(s) refused")
    return 1 if refused else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--summarize", action="store_true", help="generate en/ta/hi summaries with Claude (needs API access)")
    a = ap.parse_args()
    sys.exit(ingest(a.manifest, a.dry_run, a.summarize))
