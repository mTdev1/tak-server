import json
import os
import ssl
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DEFAULT_PORTS = "80,8080,8089,8443,8444,8446,9000,9001,9100,9102"
PORTS = [int(p) for p in os.environ.get("PORTS", DEFAULT_PORTS).replace(";", ",").split(",") if p.strip()]

# Ports wrapped in TLS (self-signed cert generated at image build time).
TLS_PORTS = {int(p) for p in os.environ.get("TLS_PORTS", "8443,8444,8446").replace(";", ",").split(",") if p.strip()}
CERT_FILE = os.environ.get("CERT_FILE", "/app/cert.pem")
KEY_FILE = os.environ.get("KEY_FILE", "/app/key.pem")

# Ports that serve the HTML hello page on GET/HEAD; all others always return JSON.
HTML_PORTS = {80}

HELLO_PAGE = b"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>Hello World</title></head>
<body><h1>Hello, World!</h1></body>
</html>
"""


class EchoHandler(BaseHTTPRequestHandler):
    def _handle(self):
        port = self.server.server_address[1]
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""

        print(f"\n--- [:{port}] {self.command} {self.path} from {self.client_address[0]}", flush=True)
        for name, value in self.headers.items():
            print(f"{name}: {value}", flush=True)
        if body:
            print(f"\n{body}", flush=True)

        if port in HTML_PORTS and self.command in ("GET", "HEAD"):
            self._send(HELLO_PAGE, "text/html; charset=utf-8")
            return

        payload = json.dumps({
            "port": port,
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers.items()),
            "body": body,
        }, indent=2).encode()
        self._send(payload, "application/json")

    def _send(self, payload, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = _handle


def make_server(port, tls_context):
    server = ThreadingHTTPServer(("0.0.0.0", port), EchoHandler)
    if port in TLS_PORTS:
        server.socket = tls_context.wrap_socket(server.socket, server_side=True, do_handshake_on_connect=False)
    return server


if __name__ == "__main__":
    tls_context = None
    if TLS_PORTS & set(PORTS):
        tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls_context.load_cert_chain(CERT_FILE, KEY_FILE)
    servers = [make_server(port, tls_context) for port in PORTS]
    for server in servers[1:]:
        threading.Thread(target=server.serve_forever, daemon=True).start()
    listening = ", ".join(f"{'https' if p in TLS_PORTS else 'http'}:{p}" for p in PORTS)
    print(f"Echo server listening on: {listening}", flush=True)
    servers[0].serve_forever()
