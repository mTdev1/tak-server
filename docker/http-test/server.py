import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8080"))


class EchoHandler(BaseHTTPRequestHandler):
    def _handle(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""

        print(f"\n--- {self.command} {self.path} from {self.client_address[0]}", flush=True)
        for name, value in self.headers.items():
            print(f"{name}: {value}", flush=True)
        if body:
            print(f"\n{body}", flush=True)

        payload = json.dumps({
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers.items()),
            "body": body,
        }, indent=2).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = _handle


if __name__ == "__main__":
    print(f"HTTP echo server listening on :{PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), EchoHandler).serve_forever()
