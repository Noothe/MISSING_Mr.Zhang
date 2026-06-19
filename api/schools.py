from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from app.server import json_response, load_school_payload


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        query = parse_qs(urlparse(self.path).query)
        province = (query.get("province") or [""])[0].strip()
        keyword = (query.get("q") or [""])[0].strip().lower()
        payload = load_school_payload()
        schools = []
        for item in payload.get("schools") or []:
            text = json.dumps(item, ensure_ascii=False).lower()
            if province and item.get("province") != province:
                continue
            if keyword and keyword not in text:
                continue
            schools.append(item)
        json_response(
            self,
            {
                "source": payload.get("source"),
                "license": payload.get("license"),
                "syncedAt": payload.get("syncedAt"),
                "schools": schools[:100],
            },
        )
