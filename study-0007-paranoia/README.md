# study-0007-paranoia — Happy Citizen Screening

A single-page, fully client-side demo for the [TypeSafe System One API](https://docs.typesafe.ai/introduction/quickstart)
(`jev-latest`), themed on the dystopian world of **PARANOIA** (the tabletop RPG by
Greg Costikyan, Dan Gelber and Eric Goldberg; *Paranoia-O* is the unofficial
online house-rules variant). Type anything, and Friend Computer judges — live,
on every keystroke — whether the utterance is acceptable from a happy, loyal
citizen of Alpha Complex.

## Features

- **Live Score evaluation** — every keystroke in the prompt box fires a
  `POST /v1/systemone` request after a 180 ms debounce (same cadence as
  study-0003). Only the newest response is rendered; superseded responses are
  discarded.
- **Configurable citizen clearance** — a selector sets *your* security
  clearance (INFRARED … ULTRAVIOLET, default RED). It is sent to the model as
  `state.citizen_clearance`, so the same utterance is judged differently per
  clearance: knowledge or privileges above your clearance are treason for you
  even when they would be routine from an Ultraviolet. Changing the selection
  re-audits the current text. Verdict texts are templated with your clearance
  ("a RED citizen is expected to be fully happy…").
- **Single `score` question** — one Score question rates the utterance on six
  ordered levels, from *Overt treason* (doubting The Computer, commie/mutant/
  secret-society sympathy, unhappiness, above-clearance knowledge) up to
  *Exemplary* (praising The Computer, reporting traitors). The answer's `score`,
  `confidence` and per-level `probabilities` drive the whole UI.
- **Clearance-colored background** — the fractional score is interpolated
  across PARANOIA's nine security clearances
  (INFRARED black → RED → ORANGE → YELLOW → GREEN → BLUE → INDIGO → VIOLET →
  ULTRAVIOLET white) and applied to the page background, a spectrum strip and
  the verdict box. In the fiction, clearance is exactly "how much The Computer
  trusts you". Page text flips light/dark for contrast.
- **INFRARED-rated controls** — citizen-operated surfaces (credentials,
  clearance selector, utterance box) are black, because white panels would be
  ULTRAVIOLET equipment that lower clearances may not legally touch.
- **Friend Computer verdicts** — each clearance band speaks in The Computer's
  voice ("TRAITOR. Report to the nearest termination booth…", "Happiness is
  mandatory", …).
- **Treason stars** — entering the treason zone (INFRARED/RED) adds one treason
  star to your loyalty rating, matching the tabletop rule. Five stars trigger a
  full-screen TERMINATED flash and the count resets.
- **The Computer's eye opens with danger** — an SVG eye in the verdict panel
  opens wider as the score drops (contented citizens barely warrant attention);
  eyelid aperture is driven continuously by the fractional score.
- **ZAP + clone delivery** — an INFRARED-band verdict fires a full-screen
  ⚡ZAP⚡, blanks the utterance box, and delivers the next clone citizen
  (the prompt card re-materializes with a delivery animation). Clone stock is
  3 per batch (`MAX_CLONES`); the third zap is a FINAL CLONE termination,
  after which a fresh batch is issued.
- **Compact stats bar** — state, last RTT, n, mean, min, max, token usage,
  stale (superseded) responses and error count.
- **No API-key persistence** — the key lives only in the page's JavaScript
  context and is wiped on reload. Nothing is written to `localStorage`,
  cookies, or files.
- **Tiled background** — a generated Friend Computer eye illustration tiles the
  page diagonally at low opacity.

## Quick start

```sh
cd study-0007-paranoia
python3 serve.py          # serves the page + proxies /api/* -> api.typesafe.ai
# open http://localhost:8000
```

`serve.py` is identical to study-0001's: stdlib-only, bound to 127.0.0.1,
relaying `/api/*` to `api.typesafe.ai` so browser calls with an `Authorization`
header pass CORS.

## Files

| File | Description |
| --- | --- |
| `index.html` | Entire app: markup, styles and logic in one file (no build, no dependencies) |
| `friend-computer.png` | Generated Friend Computer eye illustration used as the diagonally-tiled page background |
| `serve.py` | Stdlib-only static server + `/api/*` proxy bound to 127.0.0.1 |
