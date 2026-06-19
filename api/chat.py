from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from app.server import call_deepseek, json_response, read_json_body


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            payload = read_json_body(self)
            messages = payload.get("messages")
            profile = payload.get("profile") if isinstance(payload.get("profile"), dict) else {}
            if not isinstance(messages, list):
                raise ValueError("messages 必须是数组")

            clean_messages = []
            for item in messages[-12:]:
                if not isinstance(item, dict):
                    continue
                role = item.get("role")
                content = str(item.get("content") or "").strip()
                if role in {"user", "assistant"} and content:
                    clean_messages.append({"role": role, "content": content})
            if not clean_messages:
                raise ValueError("至少需要一条用户消息")

            json_response(self, call_deepseek(clean_messages, profile))
        except Exception as exc:
            json_response(self, {"error": str(exc)}, 400)
