# Pacific Vector — Brand Identity v2 (Design Notes)

## Concept
"Editorial Intelligence with a light touch of Cablegram." The mark is a single
directional arrow/vector — referencing both the product name ("Vector") and the
idea of a signal travelling toward the reader. Everything else (grid texture,
metadata lines, hairline rules) reinforces a "transmission/dispatch" feel without
relying on retro typewriter gimmicks.

## Assets produced
- `wordmark-dark.png` / `wordmark-light.png` — primary horizontal wordmark, "PACIFIC VECTOR"
- `mark-dark-v2.svg` + rasters (`mark-v2-256/32/16.png`) — compact vector/signal mark
- `favicon-16x16.png`, `favicon-32x32.png`, `favicon.ico`, `apple-touch-icon.png` (180x180)
- `og-dark.png`, `og-light.png` — 1200x630 social masthead, dark navy and cable-paper versions

## Logo / mark
The mark is one shape: a thick diagonal bar with a triangular arrowhead, set on a
rounded-square tile. No letterforms — it reads as "signal moving up and to the
right" (a vector), which doubles as a directional/intelligence cue. At 16px it
still reads unambiguously as an arrow/chevron because the silhouette is a single
solid mass with no internal gaps or thin strokes. Flat, monochrome two-tone (tile +
arrow), no shadows or gradients — holds up in browser tabs, app icons, and as a
small mark next to the wordmark in the masthead.

## Wordmark
Set in Liberation Sans Bold (a close, freely-available stand-in for Source Sans
3 / Inter / Libre Franklin — swap for IBM Plex Sans or Source Sans 3 in production
if licensing one of those is preferred). "PACIFIC" in the primary text colour,
"VECTOR" in the signal-blue accent — a restrained two-colour treatment that gives
the second word a little lift without resorting to heavy tracking or competing
glyphs. Letter-spacing is minimal (kerning +1), so it stays legible as a wordmark
at header size, unlike the wide-tracked draft 1.

## Masthead / OG image (1200x630)
Centre-left composition, single dominant identity block (mark + wordmark side by
side), built around two horizontal rules:
- **Top metadata line**: "JAPAN GEOPOLITICAL INTELLIGENCE" — small caps, wide
  tracking, muted steel-blue. This is the only place heavy letter-spacing is used,
  which is appropriate for a dateline/classification-style label.
- **Identity block**: mark + "PACIFIC VECTOR" wordmark, large and unambiguous.
- **Tagline**: "Japan geopolitical intelligence, every morning." — full-weight
  primary text colour, sets the product promise in plain language.
- **Explainer**: "A daily intelligence brief on Japan, China, the US-Japan
  alliance, and the Indo-Pacific." — secondary colour, smaller, two lines.
- **Footer metadata**: "DAILY BRIEF · TOKYO · 0600 JST" (left) and
  "PACIFIC-VECTOR.COM" (right) — same tracked-caps treatment as the top line,
  bookending the card like a cable header/footer.

## Texture
A fine dot grid covers the full canvas at low contrast (navy dots on navy bg /
grey-blue dots on cable-paper bg) — present enough to suggest coordinates or
signal traffic, but well below the contrast of the text, so it never competes for
attention. Two thin horizontal rules frame the central content block, echoing a
telegram form's ruled fields without spelling it out literally.

## Colour palettes

**Dark navy**
- Background: `#16263A`
- Primary text (warm off-white): `#F2EDE4`
- Secondary text (muted steel-blue): `#8FA3B8` / `#9FB3C8`
- Accent (signal blue): `#6FA0D6`
- Rules / grid: `#2E4A66`

**Light "cable-paper"**
- Background: `#F4F1EA`
- Primary text (deep navy): `#1A2E44`
- Secondary text (steel-blue-grey): `#6B7A8C`
- Accent (signal blue): `#3D6FA0`
- Rules / grid: `#D8DEE6`

The light version isn't aged/sepia — it's a clean warm paper tone that keeps the
same navy/blue hierarchy as the dark version, just inverted, so the two variants
read as one system rather than two different brands.

## Why it works small
The favicon/app-icon mark is a single filled shape (bar + triangle) with generous
padding inside a rounded tile — no thin strokes, no internal counters, no text. At
16px it survives as a clean arrow silhouette; at 32px and 180px the same file
scales up cleanly with no re-drawing needed. The wordmark is only used at sizes
≥ ~24px (site header, masthead), where Liberation Sans Bold at minimal tracking
stays crisp and fully legible.

## Notes / open items
- Liberation Sans is used as a stand-in because IBM Plex Sans / Source Sans 3 /
  Inter / Libre Franklin aren't installed in this environment. Recommend swapping
  to **Source Sans 3** or **IBM Plex Sans** (both open, Google Fonts) when wiring
  this into the live site — same weight/spacing should carry over directly.
- Footer metadata uses "." as a separator instead of "·" for raster-rendering
  reliability in this environment; swap to "·" in the live HTML/CSS where real
  fonts render correctly.
