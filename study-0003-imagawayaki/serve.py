#!/usr/bin/env python3
"""Static file server + same-origin /api/* proxy to https://api.typesafe.ai.

Why a proxy: api.typesafe.ai returns no Access-Control-Allow-Origin for
arbitrary origins, so a browser fetch carrying an Authorization header is
blocked at the CORS preflight. Relaying /api/* same-origin keeps the page
fully client-side while the actual HTTPS call happens server-side.

Stdlib only. Binds to 127.0.0.1 — API keys never leave the local machine
except over the genuine TLS connection to api.typesafe.ai.

Usage: python3 serve.py [port]   (default 8000)
"""

import http.server
import os
import sys
import urllib.error
import urllib.request

API_BASE = "https://api.typesafe.ai"
API_PREFIX = "/api"
ROOT = os.path.dirname(os.path.abspath(__file__))
FORWARD_HEADERS = ("Authorization", "Content-Type", "Accept", "X-Typesafe-Organization-ID")
HOP_HEADERS = {
    "transfer-encoding", "connection", "content-encoding", "content-length",
    "server", "date", "keep-alive", "upgrade",
}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def _dispatch(self):
        if self.path.startswith(API_PREFIX + "/"):
            self._proxy()
        elif self.command in ("GET", "HEAD"):
            super().do_GET()
        else:
            self.send_error(405, "Method Not Allowed")

    do_GET = _dispatch
    do_HEAD = _dispatch
    do_POST = _dispatch
    do_PUT = _dispatch
    do_PATCH = _dispatch
    do_DELETE = _dispatch
    do_OPTIONS = _dispatch

    def _proxy(self):
        upstream = API_BASE + self.path[len(API_PREFIX):]
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        req = urllib.request.Request(upstream, data=body, method=self.command)
        for name in FORWARD_HEADERS:
            value = self.headers.get(name)
            if value:
                req.add_header(name, value)
        req.add_header("Accept-Encoding", "identity")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                self._relay(resp.status, resp.headers, resp.read())
        except urllib.error.HTTPError as e:
            self._relay(e.code, e.headers, e.read())
        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")

    def _relay(self, status, headers, payload):
        self.send_response(status)
        for key, value in headers.items():
            if key.lower() not in HOP_HEADERS:
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving on http://localhost:{port}  (proxying {API_PREFIX}/* -> {API_BASE}/*)")
    server.serve_forever()
