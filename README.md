# Velan — voice-first helper for farmers & citizens

Speak in Tamil, Hindi or English. Velan explains the scheme, tells you which documents to bring,
fills the application with you one question at a time, reads it back, and gives you a printable
form, a reference number and a follow-up date.

Built for the Scaler × Wispr Flow voice-first hackathon. The **core is domain-agnostic**: everything
specific to a problem lives in `domains/` as data, so the Round 2 problem statement becomes a new
domain pack, not a rewrite.

## Run it

With Docker (no keys and no `.env` file needed):

```bash
docker compose up --build
```

Open **http://localhost:3000** in Chrome. Tap the mic, speak, tap again to stop. Without keys
Velan runs in basic offline mode and says so on screen; the main services work fully.

Optional keys: copy `.env.example` to `.env` and fill in only what you have, then run
`docker compose up --build` again.

Without Docker (Python 3.10+):

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 3000
```

Voice input needs Chrome (best on Android for Tamil/Hindi) and a page served from `localhost`
or HTTPS, because browsers only allow the microphone there.

**Try this first (the core flow):** choose தமிழ் and say *"நேற்று மழையில் என் நெல் சேதமானது,
ரெண்டு ஏக்கர்"* ("rain damaged my paddy yesterday, two acres"). Velan says the 72-hour
insurance deadline first, keeps the date, cause and acreage you already gave, asks the rest one
question at a time, reads numbers back digit by digit, reads the whole claim back, and only then
prepares it with a reference number and a printable form.

```bash
python -m pytest -q
```

### Modes

| Setting | What you get |
|---|---|
| No keys | **Offline agent** — keyword routing + step-by-step forms. Works with no internet for the AI part; good as a demo safety net. |
| `ANTHROPIC_API_KEY` | **Claude agent** (`claude-opus-5-5`, low effort for snappy voice turns) — understands free, code-mixed speech ("en peru Murugan, Erode district, 5 HP solar venum"), fills several fields from one sentence, transliterates names into English for the form. Falls back to offline for a turn if the API is unreachable. |
| `SARVAM_API_KEY` | Server-side Indic speech-to-text and natural Indian voices (Sarvam). Without it the browser's own speech recognition and voices are used. |

## How it's built

```
app/
  main.py               FastAPI: /api/session, /api/chat, /api/stt, /api/tts, /api/applications/{id}/print
  core/
    domains.py          loads domain packs; knowledge search that works across Tamil/Hindi/English
    forms.py            schema-driven form engine: validation, Aadhaar masking, read-back, printable HTML
    eligibility.py      declarative "which schemes can I claim" rules with reasons
    actions.py          the actions both agents use (start form, set fields, confirm, submit, track…)
    claude_agent.py     Claude tool-use loop over those actions
    offline_agent.py    rule-based agent over the same actions
    tracker.py          SQLite: applications, status, follow-up dates
    speech.py           optional Sarvam STT/TTS
    text.py             Indic digits, yes/no/cancel in 3 languages, spoken numbers
domains/
  _common/              shared fields (name, phone, Aadhaar, village, survey no…) + eligibility profile
  farmer/               13 services: drip, PM-KISAN, crop insurance, solar pump, farm power, KCC,
                        soil health, native seeds, season planner, organic inputs, pest help,
                        native breeds, storage & pledge loans
  citizen/              income certificate, pensions, grievance, RTI
web/                    PWA: big mic button, language switch, live form bar, read-back, cards
```

Safety rules enforced by the engine, not just the prompt:
- a form **cannot be submitted** until it has been read back and the user said yes;
- Aadhaar is stored as `XXXX-XXXX-1234` only;
- every answer is validated (10-digit mobile, past dates for crop loss, number ranges, choices);
- knowledge marked `"verified": false` is shown with "verify at office".

## Two paths, side by side: conventional and organic

Velan doesn't preach one way of farming. For nutrition, seeds, pests, poultry and livestock it
gives the **common (conventional) practice** and the **organic / natural practice** (Nammalvar's
methods) next to each other, each with its strengths **and its side effects**, and lets the
farmer choose. If a farmer says "I only want organic" (or "just tell me the chemical dose"),
the Claude agent remembers that preference and leads with it.

| Article | What it compares |
|---|---|
| `compare_soil_nutrition` | Chemical fertiliser vs compost / green manure / jeevamirtham; soil, water, pest, cost and yield effects; the middle path |
| `compare_seeds` | Native vs improved (TNAU) vs hybrid vs GM: seed saving, input needs, Bt cotton facts, illegal HTBt seed |
| `compare_pest_control` | Chemical pesticides vs traps / neem / herbal repellents / bio-agents |
| `poultry_country_chicken` | Country chicken vs commercial broiler/layer |
| `integrated_farming` | Crops + cattle + goats + poultry + fish + trees; native vs crossbred cattle |
| `nammalvar_teachings`, `nammalvar_preparations` | His principles; amirtha karaisal, fish amino acid, thema mor, herbal pest repellent |

## Adding Nammalvar's books, talks and videos (with permission)

His books, recorded talks and documentaries are copyrighted by their publishers and creators, so
the app loads them only after the rights holders agree:

1. Get written permission (Vanagam / Nammalvar Ecological Foundation, the publishers, the video
   owners). Note who granted it, the date and the scope.
2. Put the text in `sources/raw/`: book text as `.txt`, PDFs (`pip install pypdf`; scanned
   books need OCR first), video subtitles/transcripts as `.srt` / `.vtt` / `.txt`.
3. Copy `sources/manifest.example.json` to `sources/manifest.json` and fill in one entry per
   source, **including the `permission` block**. Entries without it are refused.
4. `python scripts/ingest.py sources/manifest.json --dry-run`, then run it without `--dry-run`
   (add `--summarize` to generate Tamil/Hindi/English spoken summaries with Claude).
5. Review the generated `src_*.md` articles with someone who knows his teachings, then set
   `"verified": true`.

Every generated article carries the attribution line ("Used with permission of …") and the
assistant credits him when it uses his methods. `sources/raw/` and `sources/manifest.json` are
git-ignored so licensed material isn't pushed to a public repo by accident.

## Adapting to the Round 2 problem statement

1. `mkdir domains/<new>` with `domain.json`, `forms/*.json`, `knowledge/*.md`, optional `schemes.json`
   (copy the `farmer` pack's shape).
2. `VELAN_DOMAINS=<new>,citizen` in `.env`.
3. Add a test like `test_full_drip_application_in_tamil` for the main flow.

No Python changes are needed for a new set of services, forms, eligibility rules or knowledge.

## Before the demo — content checklist

The knowledge base is **sample content written from public scheme guidelines**; most articles are
marked `verified: false`. Before judging, confirm the current numbers (subsidy %, fees, limits,
portals) against the Tamil Nadu agriculture / horticulture department, TNAU Agritech and the scheme
portals, then flip `verified` to `true`. Record a few farmers and native-breed/seed dealers
describing their practices (by voice) and add them as knowledge articles; the dealer directory in
`tn_native_breeds.md` is a placeholder until dealers are verified.

## Known gaps / next steps

- Offline mode keeps names in the script they were spoken in; the Claude agent transliterates.
- Reminders are stored (follow-up date) but not yet sent — add SMS/WhatsApp (e.g. a daily job over
  `tracker.list`).
- WhatsApp voice-note channel and IVR phone line: the `/api/chat` contract is channel-independent,
  so these are thin adapters.
- Document photo → OCR check (name/survey number match) is not built yet.
- Sessions are in memory; use Redis or the DB if you run more than one server process.
