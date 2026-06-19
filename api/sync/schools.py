from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from app.server import SYNC_TOKEN, fetch_authorized_school_source, json_response


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            if SYNC_TOKEN and self.headers.get("X-Sync-Token") != SYNC_TOKEN:
                json_response(self, {"error": "同步 token 不正确"}, 403)
                return
            json_response(self, fetch_authorized_school_source())
        except Exception as exc:
            json_response(self, {"error": str(exc)}, 400)
