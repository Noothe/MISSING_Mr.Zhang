from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler

from app.server import DEEPSEEK_MODEL, SCHOOL_SOURCE_URL, json_response


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        json_response(
            self,
            {
                "ok": True,
                "runtime": "vercel-python",
                "model": DEEPSEEK_MODEL,
                "hasDeepSeekKey": bool(os.getenv("DEEPSEEK_API_KEY")),
                "hasSchoolSource": bool(SCHOOL_SOURCE_URL),
            },
        )
