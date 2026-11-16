import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .constants import PORT


def start_server(manager):
    """Запускає локальний приймач даних від розширення. Кидає OSError, якщо порт зайнятий."""

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            ctype = self.headers.get("Content-Type", "").split(";")[0].strip()
            # application/json змушує браузер робити preflight, тож
            # звичайні сайти не зможуть підсунути сюди дані
            if self.path != "/update" or ctype != "application/json":
                self.send_response(400)
                self.end_headers()
                return
            try:
                size = min(int(self.headers.get("Content-Length", 0)), 65536)
                manager.push_media(json.loads(self.rfile.read(size)))
                self.send_response(204)
            except Exception:
                self.send_response(400)
            self.end_headers()

        def log_message(self, *args):
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd
