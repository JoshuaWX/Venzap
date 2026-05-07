from __future__ import annotations

import http.server
import os
import socketserver
import sys
from pathlib import Path
from threading import Thread


class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path in {"/", "/health"}:
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def _serve_health(port: int) -> socketserver.TCPServer:
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = ReusableTCPServer(("0.0.0.0", port), HealthHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main() -> None:
    port = int(os.environ.get("PORT", "10000"))
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    from bot.main import main as run_bot

    server = _serve_health(port)
    try:
        run_bot()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
