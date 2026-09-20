# study-0004-handwriting — handwritten character classifier

A single-page, fully client-side demo for the [TypeSafe System One API](https://docs.typesafe.ai/introduction/quickstart)
(`jev-latest`). Draw a character on the pad and Jev classifies it against the
36 candidates `0-9` and `A-Z`. When the top probability clears the commit
threshold, the character is appended to the recognized text and the pad clears
itself for the next one.

Jev accepts **text only** — images are not supported. So this demo rasterizes
the ink into a 24×24 ASCII bitmap (`#` = ink, `.` = blank) and sends that as the
`state`. One `choice` question carries all 36 candidates; each criterion is a
short shape hint that doubles as a disambiguation aid for confusable pairs
(0/O, 1/I, 2/Z, 5/S, 6/G, 8/B, 7/T). Recognizing characters from ASCII art is
the actual experiment here — accuracy depends on how well Jev reads the
rasterization.

## Features

- **Drawing pad** — pointer-events canvas (mouse, pen, touch), 300 px, with a
  faint guide grid. Strokes are captured incrementally; `pointerdown` cancels a
  pending classification so multi-stroke characters (K, E, 4, …) are not
  committed half-drawn.
- **Auto-classify on pause** — a request fires 650 ms after the pen is lifted.
  Multi-stroke input just needs each next stroke to start inside that window.
- **ASCII-art state** — the ink's bounding box is cropped, aspect-fit into a
  96×96 work canvas, then downsampled to a 24×24 grid (a cell is ink when ≥20%
  of its 4×4 block is covered). The exact raster sent to the model can be
  inspected in the collapsible preview.
- **Commit on confidence** — if the top candidate's probability reaches the
  threshold (slider, 10–95%, default 60%), the character is committed, the pad
  flashes green and clears. Below-threshold results flash amber and stay on the
  pad so you can add strokes.
- **Recognized text** — monospace output line with Backspace, Copy and Clear.
- **Single `choice` question, top-10 ranking** — the answer's `probabilities`
  map drives an animated bar list; candidates under the threshold are muted.
- **Compact stats bar** — state, last RTT, n, mean, min, max, token usage,
  stale (superseded) responses and error count.
- **No API-key persistence** — the key lives only in the page's JavaScript
  context and is wiped on reload. Nothing is written to `localStorage`,
  cookies, or files.

## Quick start

```sh
cd study-0004-handwriting
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
| `serve.py` | Stdlib-only static server + `/api/*` proxy bound to 127.0.0.1 |
