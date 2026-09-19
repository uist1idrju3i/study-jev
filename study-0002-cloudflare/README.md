# study-0002-cloudflare — Jev on Cloudflare Workers AI

A single-page, fully client-side demo for [`typesafe/jev`](https://developers.cloudflare.com/ai/models/typesafe/jev/)
hosted on Cloudflare Workers AI, built around per-address-family RTT (round-trip
time) measurement of the Cloudflare endpoint.

## Features

- **Jev demo call** — send `state` + typed questions (`noul` / `choice` / `score`) to
  `POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run` with
  `{"model": "typesafe/jev", "input": {...}}` and inspect the structured answers.
- **IPv4/IPv6 selection** — `api.cloudflare.com` is dual-stack, but browsers cannot
  choose the address family of `fetch()`. `serve.py` resolves the host restricted to
  the requested family and connects with correct SNI/Host, for both RTT sampling and
  the demo call (`?family=4|6` on `/api/*`).
- **Precise RTT measurement** — timed inside `serve.py` with `time.perf_counter()`:
  DNS, TCP connect, TLS handshake, TTFB and total. Connections are reused via
  HTTP/1.1 keep-alive (warmup excluded from stats); an optional checkbox forces a
  fresh TCP+TLS handshake per sample.
- **Statistics** — live table of n, min, mean, median, p90, p95, max, stddev and
  jitter, a canvas chart, and CSV export including per-phase timings.
- **No credential persistence** — the API token and Account ID live only in the
  page's JavaScript context and are wiped on reload. Nothing is written to
  `localStorage`, cookies, or files.

## Quick start

```sh
cd study-0002-cloudflare
python3 serve.py   # serves the page, proxies /api/*, answers /rtt
# open http://localhost:8000
```

`serve.py` uses only the Python standard library.

## Why the proxy exists

Browsers cannot call `api.cloudflare.com` directly: the API answers the CORS
preflight with `405` and returns no `Access-Control-Allow-Origin`, so any request
carrying an `Authorization` header fails before it is even sent. `serve.py`
serves the page and relays same-origin `/api/*` requests to the official endpoint
over normal TLS — credentials only ever travel between your browser and your own
localhost process, then straight to Cloudflare.

Note that `python3 -m http.server 8000` serves the page but cannot proxy, so the
Jev demo call still fails CORS without `serve.py`.

## RTT measurement notes

- `GET /rtt?family=4|6|auto&keepalive=0|1` performs one upstream request and
  returns JSON: `{ok, family, ip, reused, dns_ms, tcp_ms, tls_ms, ttfb_ms,
  total_ms, status}`.
- The stats use `total_ms` (request sent → last byte), measured inside the proxy
  — no browser or localhost-hop noise.
- On a host without IPv6 routing, `family=6` samples simply report the OS error
  (`Network is unreachable`), which is exactly the comparison this tool is for.
- To measure with the handshake included every time, tick "fresh TCP+TLS
  connection per sample".

## Files

| File | Description |
| --- | --- |
| `index.html` | Entire app: markup, styles and logic in one file (no build, no dependencies) |
| `serve.py` | Stdlib-only static server + `/api/*` proxy + `/rtt` family-pinned measurement, bound to 127.0.0.1 |
