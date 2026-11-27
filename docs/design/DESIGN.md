# Velan design profile

The visual guide with live examples is `velan-design-profile.html` (open it in a browser). This
file is the short version to follow when building any Velan screen, slide or page.

**Sources of inspiration (techniques only, nothing copied):**
- **trycontour.com:** calm paper-and-ink editorial look, two-tone headlines, topographic line art,
  square quiet buttons with an arrow box, long soft shadows, a live transcript card.
- **The layered web style guide:** art → grain → scrim → glass layers, seams between sections, a
  single colour story, slow ambient motion and reduced-motion support.

**Velan's own twist:** kolam line art replaces contour lines; turmeric, kumkum and leaf replace a
generic palette; Tamil leads every screen.

## Colour (Turmeric dawn, the default story)

| Token | Hex | Use |
|---|---|---|
| `--paper` | `#F5F0E6` | page background |
| `--paper-2` | `#FBF8F1` | cards, inputs |
| `--sand` | `#E8E0CF` | alternate section bands |
| `--ink` | `#153C25` | text, primary buttons, done steps |
| `--ink-deep` | `#00321C` | ribbon, button fill |
| `--sage` | `#5E6D63` | second headline line, labels, quiet text |
| `--mist` | `#DCE5DA` | "written to…" footers, soft highlights |
| `--accent` (turmeric) | `#D9952B` | ONE accent: mic rim, reply thread, current step |
| `--alert` (kumkum) | `#B23A2A` | deadlines, errors, listening state only |
| `--signal` | `#20A04E` | live dot, done |

Other stories:
- **Leaf monsoon:** cooler greens.
- **Temple night:** the dark mode, with lamp-gold accent `#F0B54A` on `#10190F`.

Rules: text holds 4.5:1 contrast on its background, and status colours are never the only signal
(always say it in words too).

## Type
- **Public Sans** for the interface (weights 400/500/600). **Hind Madurai** for Tamil. **Spectral**
  only for "printed" moments such as reference numbers and quotes.
- **Headlines:** weight 500, letter-spacing −0.025em, line-height 1.08. Two tones: the first line
  in ink, the second in sage (`.soft`). Never all caps.
- **App scale:** latest reply 20–22px (Tamil); body 17px; labels 13–14px in sage.
- **Deck scale:** 120 / 72 / 44 / 32 / 24.
- **Tamil leads:** English follows smaller beneath it.

## Layers and texture
1. **Paper:** one flat tone per section; alternate paper and sand bands.
2. **Kolam line art:** pulli dots plus loops, line colour at 10–13% ink. Fractal-noise grain at 18%
   `multiply` (8% `screen` in Temple night).
3. **Scrim:** a paper-coloured ellipse behind every headline. Each section's gradient ends in the
   next section's colour, so sections meet in seams, not hard edges.
4. **Glass:** the nav and floating cards use `backdrop-filter: blur(12px)` over 82% paper.

## Shapes and shadows
- Panels have 14px corners, controls 4px, pills only for small chips. The mic is the one round,
  rich object.
- **Shadows:** long and soft, `0 30px 60px -40px` (float) or `0 24px 48px -32px` (card), in ink. No
  hard drop shadows.

## Components
- **Mic:** 104–112px, ink with a turmeric rim and a dotted kolam ring that turns slowly (42s).
  Listening turns it kumkum with a 6s ring and kumkum sound bars.
- **Reply:** the latest turn is the biggest text on screen, on paper with a turmeric thread down
  the left edge. Older turns go in a History drawer.
- **Live call card:** a header with a green ping dot and "Live", the turns (Tamil plus an English
  gloss), and a mist footer stating what was written. Use it in marketing and the demo.
- **Step tracker:** segments in ink (done), turmeric (now) and faint ink (later), with a sage
  label such as "Next: Village · 4 of 8".
- **Service tile:** a thin line icon (1.5px stroke) with a Tamil name and a quoted example
  sentence. Emoji are acceptable in the prototype only.
- **Deadline:** a kumkum rule on the left plus the words. **Receipt:** the reference number set in
  Spectral.
- **Buttons:** 4px corners, an arrow box on primary actions, 56px tall in the app. A
  confirmation always offers "change" next to "yes".

## Motion
- **Entrances play once:** easing `cubic-bezier(.16,1,.3,1)`; nav, then headline, then line, then
  card, 150ms apart.
- **Ambient motion is slow:** the kolam ring takes 42s, the live ping 1.8s, the marquee 48s.
  Kolam line art draws itself in over 4–6s on first view.
- Animate only `transform` and `opacity`. `prefers-reduced-motion` turns everything off.

## Voice and copy
- Tamil first, everyday spoken words, respectful forms (நீங்கள்).
- One idea per line: deadlines first, then documents, then one question at a time.
- Never alarming, never preachy. Farming advice always shows both paths (conventional and
  organic) with their side effects.
