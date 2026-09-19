# study-0001-rtt — Jev RTT demo

A single-page, fully client-side demo for the [TypeSafe System One API](https://docs.typesafe.ai/introduction/quickstart)
(`jev-latest`), built around precise RTT (round-trip time) measurement of the official endpoint.

## Features

- **Jev demo call** — send `state` + typed questions (`noul` / `choice` / `score`) to
  `POST https://api.typesafe.ai/v1/systemone` and inspect the structured answers.
- **Precise RTT measurement** — repeated requests to the API endpoint timed with
  `performance.now()`, with warmup exclusion and a configurable sample count / interval.
- **Statistics** — live table of n, min, mean, median, p90, p95, max, stddev and jitter
  (mean |Δ| between consecutive samples), a canvas chart, and CSV export.
- **No API-key persistence** — the key lives only in the page's JavaScript context and is
  wiped on reload. Nothing is written to `localStorage`, cookies, or files.
- **IPv4 only** — `api.typesafe.ai` publishes no AAAA record, so IPv6 measurement is not
  possible; the RTT section measures the IPv4 path (per project decision, no IPv6 target).

## Quick start

```sh
cd study-0001-rtt
python3 serve.py          # serves the page + proxies /api/* -> api.typesafe.ai
# open http://localhost:8000
```

`serve.py` uses only the Python standard library.

## Why the proxy exists

Browsers cannot call `api.typesafe.ai` directly: the API returns no
`Access-Control-Allow-Origin` for arbitrary origins, so any request carrying an
`Authorization` header fails the CORS preflight (`TypeError: Failed to fetch`) before it
is even sent. `serve.py` serves the page and relays same-origin `/api/*` requests to the
official endpoint over normal TLS — the key only ever travels between your browser and
your own localhost process, then straight to TypeSafe.

When the page is served by `serve.py`, the demo endpoint defaults to the relative path
`/api/v1/systemone`. Set it to `https://api.typesafe.ai/v1/systemone` to observe the raw
CORS failure (the page detects it and prints an equivalent `curl` command).

## RTT measurement notes

- The measurement uses `fetch(..., {mode: 'no-cors'})`, so no API key is needed; the
  response is opaque but the request fully round-trips the server.
- The first request includes TCP+TLS handshake; later samples reuse the keep-alive
  HTTP/2 connection. Warmup samples are discarded from the stats — raise the warmup
  count if you want purely steady-state numbers.
- To measure the *proxied* path instead, point the target at `/api/v1/systemone`.

## Files

| File | Description |
| --- | --- |
| `index.html` | Entire app: markup, styles and logic in one file (no build, no dependencies) |
| `serve.py` | Stdlib-only static server + `/api/*` proxy bound to 127.0.0.1 |
