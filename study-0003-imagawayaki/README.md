# study-0003-imagawayaki — 今川焼き name-classifier demo

A single-page, fully client-side demo for the [TypeSafe System One API](https://docs.typesafe.ai/introduction/quickstart)
(`jev-latest`), styled like a real web service. It classifies a free-text description
of a Japanese sweet into its most likely regional/product name — live, on every keystroke.

## Features

- **Live classification** — every keystroke in the prompt box fires a `POST /v1/systemone`
  request after a 180 ms debounce (the same cadence as real search-as-you-type services).
  Only the newest response is rendered; superseded responses are discarded.
- **Single `choice` question** — one Choice question carries all 73 candidates; the answer's
  `probabilities` map drives a top-10 ranking with animated bars and category tags.
- **Candidate list** — built from the Japanese Wikipedia article
  [今川焼き](https://ja.wikipedia.org/wiki/今川焼き): all entries under
  「形状や製法に基づく名称」 and 「商品名や地域による名称」, plus eight extra Kyushu/Hakata
  sweets (大原松露饅頭, 博多ぶらぶら, 名菓ひよ子, 博多の女, めんべい, 筑紫もち, 梅ヶ枝餅,
  博多通りもん) and 「未定義」 as the none-of-the-above option.
- **Compact stats bar** — one modest line: state, last RTT, n, mean, min, max, token usage,
  discarded (stale) responses and error count. No chart, no CSV.
- **No API-key persistence** — the key lives only in the page's JavaScript context and is
  wiped on reload. Nothing is written to `localStorage`, cookies, or files.
- **Japanese UI**.

## Quick start

```sh
cd study-0003-imagawayaki
python3 serve.py          # serves the page + proxies /api/* -> api.typesafe.ai
# open http://localhost:8000
```

`serve.py` is identical to study-0001's: stdlib-only, bound to 127.0.0.1, relaying
`/api/*` to `api.typesafe.ai` so browser calls with an `Authorization` header pass CORS.

## Files

| File | Description |
| --- | --- |
| `index.html` | Entire app: markup, styles and logic in one file (no build, no dependencies) |
| `serve.py` | Stdlib-only static server + `/api/*` proxy bound to 127.0.0.1 |
