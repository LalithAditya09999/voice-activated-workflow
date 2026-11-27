# Velan: project notes for Claude

Velan is a voice-first assistant (Tamil, Hindi, English) that helps farmers and citizens in Tamil
Nadu claim government benefits. It's built for the Scaler × Wispr Flow hackathon (Round 2
deadline: 30 Nov 2026).

## Design
Follow `docs/design/DESIGN.md` for every screen, slide and page. The live visual reference is
`docs/design/velan-design-profile.html`. In short:
- Calm paper (`#F5F0E6`) and forest ink (`#153C25`), with turmeric (`#D9952B`) as the single
  accent. Kumkum (`#B23A2A`) only for deadlines and errors; green (`#20A04E`) for live and done.
- Kolam line art as faint texture under a scrim. Two-tone headlines (ink, then sage).
- Public Sans, Hind Madurai for Tamil, Spectral for receipts.
- Square, quiet controls; the mic is the one round, rich object. Long soft shadows.
- Motion: entrances once, ambient slow, reduced motion honoured.

## Code
- Backend: FastAPI under `app/`. Problem-specific content is data under `domains/` (services,
  forms, eligibility rules, knowledge articles).
- Front end: `web/` (plain HTML/CSS/JS PWA, no build step).
- Run: `docker compose up --build` serves it on port 3000. It must start with no `.env` file and no
  keys (it falls back to offline mode).
- Test: `python -m pytest -q`. Keep all tests passing before pushing.
- Never commit real keys. `sources/raw/` holds licensed material and stays git-ignored.
