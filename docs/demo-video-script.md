# Velan: demo video script (target 2:50, limit 3:00)

**Format:** a screen recording of the app with your voiceover in English. You speak to the app in
Tamil on camera. Add English captions for every Tamil line.

## Before you record (10 minutes)

1. **Start fresh:** run `docker compose down -v`, then `docker compose up --build`, so no old
   applications show up.
2. **Use Chrome** at `http://localhost:3000`. Press F12, then the phone icon, and pick
   **Pixel 7** so it looks like a phone. Zoom the browser to 100%.
3. **Voices:** Chrome on Windows may have no Tamil voice. Add one in Windows Settings → Time &
   language → Speech → Add voices → Tamil, then restart Chrome. If you can't, record with
   **Voice off** and keep the captions on screen.
4. **Microphone:** use a headset mic in a quiet room. Speak at a normal pace and pause briefly
   after each answer.
5. **Recorder:** OBS or Xbox Game Bar (Win + G), capturing **your mic and the computer's sound**,
   so Velan's voice is recorded too.
6. **Rehearse:** run the full flow once without recording. If the app mishears a word, simply
   retake that step.

## Shot list

| Time | On screen | You say (voiceover) | You say to the app (Tamil) |
|---|---|---|---|
| 0:00–0:10 | Black title card: "Rain damaged Murugan's paddy yesterday. He has 72 hours to claim insurance. He can't read the form." | (silent, or soft music) | |
| 0:10–0:22 | Card: "86% of India's farms are under 2 hectares. Benefits are lost to paperwork, not eligibility." | "Small farmers lose government benefits every season, not because they aren't eligible, but because every scheme is a form, a portal and a deadline in written English." | |
| 0:22–0:32 | Velan home screen | "This is Velan. One microphone, in Tamil, Hindi or English. No reading, no typing." | |
| 0:32–0:45 | Tap the mic, speak, Velan answers | "Murugan just says what happened." | **நேற்று மழையில் என் நெல் சேதமானது, ரெண்டு ஏக்கர்** |
| 0:45–0:55 | Reply with the 72-hour deadline, then the document checklist | "Velan says the deadline first, then what to bring." | |
| 0:55–1:05 | Tap the mic | | **ஆமாம்** |
| 1:05–1:15 | Progress bar appears; Velan asks for the crop | "It kept the date, the cause and the acres he already said, so it never asks twice." | |
| 1:15–1:45 | Answer each question (jump-cut between answers) | "Then one question at a time." | **நெல்** → **வங்கி** → **முருகன்** → **98765 43210** |
| 1:45–1:55 | Velan reads the number back digit by digit | "Numbers are read back digit by digit." | **ஆமாம்** |
| 1:55–2:05 | Answer the rest (jump-cut) | | **தேனி** → **கம்பம்** → **45/2** → **ஆமாம்** |
| 2:05–2:15 | "Are these details correct?" with the list | "Everything is read back. Nothing goes ahead without a spoken yes." | **ஆமாம்** |
| 2:15–2:25 | Reference number card, then tap the print button and show the form | "A reference number, a printable form in English for the office, and a follow-up date." | |
| 2:25–2:35 | Go home and tap **🌿 Organic or chemical**; show the one-line reply | "Ask about farming and Velan gives both paths, chemical and organic, with their side effects. The farmer chooses." | |
| 2:35–2:43 | Quick cut: terminal running `docker compose up`, then the app switched to EN | "It runs with one command and no API keys, even offline. Built hands-free with Wispr Flow." | |
| 2:43–2:50 | End card: **Velan · வேலன் — speak, and it gets done.** "Pilot: 2,000 farm families in Theni and Madurai." Repo link. | "Velan. Speak, and it gets done." | |

**Time saving:** the answers between 1:15 and 2:05 are the slowest part. Cut out the pauses and
show each answer for about 3 seconds. If you're over 3:00, drop the organic-or-chemical shot
(2:25–2:35) first.

## Captions to add (English, for the Tamil lines)

- நேற்று மழையில் என் நெல் சேதமானது, ரெண்டு ஏக்கர் → "Rain damaged my paddy yesterday, two acres."
- சேதம் நடந்த 72 மணி நேரத்துக்குள் தெரிவிக்கவும் → "Report within 72 hours of the damage."
- ஆமாம் → "Yes"
- நெல் → "Paddy" · வங்கி → "Through the bank" · தேனி → "Theni" · கம்பம் → "Cumbum"
- இந்த விவரங்கள் சரியா? → "Are these details correct?"

## If something goes wrong

- **The app mishears a word:** stop and retake that answer. Don't switch to typing; the demo has
  to show voice.
- **"Sorry, I didn't catch that":** that's the app working correctly. You can keep it in as a
  moment that shows it doesn't guess.
- **Velan is silent:** there's no Tamil voice installed. Keep going; the captions carry it.
- **Tapping the mic does nothing:** check that Chrome has microphone permission (the lock icon in
  the address bar).

## Upload

YouTube, set to **Unlisted**, length **3:00 or less**. Title:
*Velan — voice-first government benefits for farmers (Tamil)*. In the description, put one line
about the problem, the GitHub link and "Built with Wispr Flow".
