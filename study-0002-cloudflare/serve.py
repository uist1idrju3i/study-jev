#!/usr/bin/env python3
"""Static file server + same-origin proxy to api.cloudflare.com with
per-address-family connection pinning and server-side RTT measurement.

Why a proxy: api.cloudflare.com answers CORS preflights with 405 and no
Access-Control-Allow-Origin, so a browser fetch carrying an Authorization
header is blocked before it is sent. Relaying /api/* same-origin keeps the
page fully client-side while the actual HTTPS call happens here.

IPv4/IPv6: browsers cannot choose the address family of a fetch(). To make
family selection possible, two endpoints do the connecting here:

  GET /rtt?family=4|6|auto&keepalive=0|1
      Resolve api.cloudflare.com restricted to the requested family, open a
      TLS connection (correct SNI/Host), perform a lightweight GET, and
      return per-phase timings as JSON: dns_ms, tcp_ms, tls_ms, ttfb_ms,
      total_ms. Connections are pooled per family and reused (HTTP/1.1
      keep-alive) so steady-state samples measure pure request round-trips;
      keepalive=0 forces a fresh TCP+TLS handshake per sample.

  /api/* ?family=4|6
      Proxy to https://api.cloudflare.com/* pinned to the requested family
      (default: auto). Adds X-Upstream-IP / X-Upstream-Family response
      headers so the page can show which stack carried the demo call.

Stdlib only. Binds to 127.0.0.1 — API tokens never leave the local machine
except over the genuine TLS connection to api.cloudflare.com.

Usage: python3 serve.py [port]   (default 8000)
"""

import http.client
import http.server
import json
import os
import socket
import ssl
import sys
import time
import urllib.parse

API_HOST = "api.cloudflare.com"
API_PORT = 443
API_PREFIX = "/api"
ROOT = os.path.dirname(os.path.abspath(__file__))
FORWARD_HEADERS = ("Authorization", "Content-Type", "Accept")
HOP_HEADERS = {
    "transfer-encoding", "connection", "content-encoding", "content-length",
    "server", "date", "keep-alive", "upgrade", "set-cookie",
}
FAMILIES = {"auto": socket.AF_UNSPEC, "0": socket.AF_UNSPEC,
            "4": socket.AF_INET, "6": socket.AF_INET6}
# Tiny unauthenticated API path: enough bytes for a full request round-trip.
RTT_PATH = "/client/v4/"
TIMEOUT = 30

_tls = ssl.create_default_context()
_tls.set_alpn_protocols(["http/1.1"])  # http.client only speaks HTTP/1.1

# Keep-alive pool: family name -> established FamilyHTTPSConnection.
POOL = {}


class FamilyHTTPSConnection(http.client.HTTPSConnection):
    """HTTPSConnection restricted to a single address family.

    Records the remote IP and per-phase connect timings (dns_ms, tcp_ms,
    tls_ms) so callers can report exactly which stack a request used.
    """

    def __init__(self, family):
        self._family = family
        self.remote_ip = None
        self.dns_ms = self.tcp_ms = self.tls_ms = None
        super().__init__(API_HOST, API_PORT, timeout=TIMEOUT, context=_tls)

    def connect(self):
        t0 = time.perf_counter()
        infos = socket.getaddrinfo(self.host, self.port,
                                   self._family, socket.SOCK_STREAM)
        t_dns = time.perf_counter()
        self.dns_ms = (t_dns - t0) * 1000
        sock, err = None, None
        for af, st, pr, _, sa in infos:
            try:
                sock = socket.socket(af, st, pr)
                sock.settimeout(self.timeout)
                sock.connect(sa)
                break
            except OSError as e:
                err = e
                if sock is not None:
                    sock.close()
                sock = None
        if sock is None:
            raise err or OSError("getaddrinfo returned no addresses")
        self.remote_ip = sa[0]
        t_tcp = time.perf_counter()
        self.tcp_ms = (t_tcp - t_dns) * 1000
        # SNI + Host must stay api.cloudflare.com regardless of the family.
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
        self.tls_ms = (time.perf_counter() - t_tcp) * 1000


def request_once(method, path, headers=None, body=None,
                 family=socket.AF_UNSPEC, conn=None):
    """Run one HTTPS request to API_HOST.

    Reuses `conn` when given, otherwise opens a fresh FamilyHTTPSConnection.
    Returns (conn, meta, status, response_headers, payload); meta carries
    ip/reused flags and timings in milliseconds (None when not measured).
    """
    created = conn is None
    if created:
        conn = FamilyHTTPSConnection(family)
    try:
        t0 = time.perf_counter()
        conn.request(method, path, body=body, headers=dict(headers or {}))
        resp = conn.getresponse()
        t_head = time.perf_counter()
        payload = resp.read()
        t_end = time.perf_counter()
    except Exception:
        conn.close()
        raise
    meta = {
        "reused": not created,
        "ip": conn.remote_ip,
        "dns_ms": conn.dns_ms if created else None,
        "tcp_ms": conn.tcp_ms if created else None,
        "tls_ms": conn.tls_ms if created else None,
        "ttfb_ms": (t_head - t0) * 1000,
        "total_ms": (t_end - t0) * 1000,
    }
    return conn, meta, resp.status, resp.headers, payload


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def _dispatch(self):
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path == "/rtt":
            self._rtt(urllib.parse.parse_qs(parsed.query))
        elif parsed.path.startswith(API_PREFIX + "/"):
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

    def _json(self, status, obj):
        payload = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _rtt(self, query):
        fam = (query.get("family") or ["auto"])[0]
        if fam not in FAMILIES:
            return self._json(400, {"ok": False,
                                    "error": "family must be 4, 6, or auto"})
        keepalive = (query.get("keepalive") or ["1"])[0] not in ("0", "false")
        conn = POOL.get(fam) if keepalive else None
        try:
            conn, meta, status, hdrs, _ = request_once(
                "GET", RTT_PATH, {"Accept": "application/json"},
                family=FAMILIES[fam], conn=conn)
        except Exception as e:
            POOL.pop(fam, None)
            return self._json(200, {"ok": False, "family": fam,
                                    "error": f"{type(e).__name__}: {e}"})
        meta.update(ok=True, family=fam, status=status)
        if keepalive and hdrs.get("connection", "").lower() != "close":
            POOL[fam] = conn
        else:
            conn.close()
            POOL.pop(fam, None)
        self._json(200, meta)

    def _proxy(self):
        parsed = urllib.parse.urlsplit(self.path)
        q = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        fam = next((v for k, v in q if k == "family"), "auto")
        family = FAMILIES.get(fam)
        if family is None:
            return self._json(400, {"error": "family must be 4, 6, or auto"})
        # Strip our pseudo-parameter before forwarding upstream.
        rest = urllib.parse.urlencode([(k, v) for k, v in q if k != "family"])
        upstream = parsed.path[len(API_PREFIX):] + ("?" + rest if rest else "")
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        headers = {n: self.headers[n] for n in FORWARD_HEADERS
                   if self.headers.get(n)}
        headers["Accept-Encoding"] = "identity"
        try:
            conn, meta, status, hdrs, payload = request_once(
                self.command, upstream, headers, body, family)
            conn.close()
        except Exception as e:
            return self._json(502, {"error": f"proxy error: {e}"})
        self.send_response(status)
        for key, value in hdrs.items():
            if key.lower() not in HOP_HEADERS:
                self.send_header(key, value)
        self.send_header("X-Upstream-IP", meta["ip"] or "")
        self.send_header("X-Upstream-Family", fam)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving on http://localhost:{port}  "
          f"(proxying {API_PREFIX}/* -> https://{API_HOST}/*, "
          f"/rtt measures per-family RTT)")
    server.serve_forever()
