# Demo video generator

`record.js` records the **real Velan app** going through the crop-loss flow, inside `stage.html`
(a phone frame on the kolam background, with captions and title cards). The voice input is
simulated: the script shows the mic listening and the words appearing, then sends that text. The
video says so in the corner. Splice in a short real-voice clip before you submit.

```bash
docker compose up --build            # or: uvicorn app.main:app --port 3000
npm i playwright && npx playwright install chromium   # once, if you don't have it
node tools/demo-video/record.js ./out
ffmpeg -i out/*.webm -c:v libx264 -crf 20 -pix_fmt yuv420p -r 30 velan-demo.mp4
```

Edit the captions and timings in `record.js` (the `cap(...)` and `sleep(...)` calls) and the cards
in `stage.html`.
