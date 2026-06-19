from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
DATA_DIR = APP_DIR / "data"
SEED_DATA = DATA_DIR / "schools.seed.json"
CACHE_DATA = DATA_DIR / "schools.cache.json"
SKILL_FILE = ROOT / "SKILL.md"

DEEPSEEK_ENDPOINT = os.getenv("DEEPSEEK_ENDPOINT", "https://api.deepseek.com/chat/completions")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
SCHOOL_SOURCE_URL = os.getenv("SCHOOL_SOURCE_URL", "")
SYNC_TOKEN = os.getenv("SYNC_TOKEN", "")


MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}


def read_text(path: Path, fallback: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return fallback


def json_response(handler: BaseHTTPRequestHandler, payload: Any, status: int = 200) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length") or 0)
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("请求体不是合法 JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("请求体必须是 JSON 对象")
    return payload


def load_school_payload() -> dict[str, Any]:
    source_path = CACHE_DATA if CACHE_DATA.exists() else SEED_DATA
    payload = json.loads(read_text(source_path, '{"schools": []}'))
    if not isinstance(payload, dict):
        return {"source": "invalid", "syncedAt": None, "schools": []}
    schools = payload.get("schools")
    if not isinstance(schools, list):
        payload["schools"] = []
    return payload


def normalize_school_payload(payload: Any, source_url: str) -> dict[str, Any]:
    if isinstance(payload, list):
        schools = payload
        meta: dict[str, Any] = {}
    elif isinstance(payload, dict):
        schools = payload.get("schools")
        meta = payload
    else:
        raise ValueError("院校数据源必须是数组或包含 schools 数组的对象")

    if not isinstance(schools, list):
        raise ValueError("院校数据源缺少 schools 数组")

    normalized: list[dict[str, Any]] = []
    for item in schools:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        province = str(item.get("province") or "").strip()
        if not name or not province:
            continue
        normalized.append(
            {
                "name": name,
                "province": province,
                "city": str(item.get("city") or "").strip(),
                "level": str(item.get("level") or "").strip(),
                "type": str(item.get("type") or "").strip(),
                "tags": item.get("tags") if isinstance(item.get("tags"), list) else [],
                "officialUrl": str(item.get("officialUrl") or "").strip(),
                "admissionUrl": str(item.get("admissionUrl") or "").strip(),
                "notes": str(item.get("notes") or "").strip(),
            }
        )

    if not normalized:
        raise ValueError("院校数据源没有可用记录，至少需要 name 和 province")

    return {
        "source": meta.get("source") or source_url,
        "sourceType": meta.get("sourceType") or "authorized-json",
        "license": meta.get("license") or "请在数据源中声明授权或开放许可",
        "syncedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "schools": normalized,
    }


def fetch_authorized_school_source() -> dict[str, Any]:
    if not SCHOOL_SOURCE_URL:
        raise ValueError("未配置 SCHOOL_SOURCE_URL。请使用已授权的院校 JSON 数据源，不要抓取商业网站页面。")
    request = urllib.request.Request(
        SCHOOL_SOURCE_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": "MISSING-Mr-Zhang/0.1 data-sync",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        payload = json.loads(response.read().decode(charset))
    normalized = normalize_school_payload(payload, SCHOOL_SOURCE_URL)
    CACHE_DATA.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return normalized


def build_system_prompt(school_context: str) -> str:
    skill = read_text(SKILL_FILE)
    if len(skill) > 18000:
        skill = skill[:18000] + "\n\n[SKILL 内容因上下文长度被截断，完整文件仍在仓库根目录 SKILL.md。]"

    return f"""
你是《念张师》（Missing Mr.Zhang）网站的志愿填报互动顾问。

身份边界：
- 你不是张雪峰本人，也不是其官方账号或机构；你只能使用 zhangxuefeng-skill 的公开风格和思维框架做模拟式分析。
- 必须尊重上游 skill 作者，不声称这些材料由本站原创。
- 志愿填报是高风险教育决策。你必须提醒用户最终以各省教育考试院、院校招生章程和官方投档线为准。
- 不得编造录取概率、位次、学费、招生计划、就业率或薪资。没有数据就先追问或说明需要核验。
- 不得直接复述上游 skill 中关于人物近况、生死、处罚、商业数据等时间敏感断言，除非来自当前可信来源。
- 每次涉及具体学校、专业、分数、位次、批次、政策时，先收集：省份、科类/选科、分数、位次、年份、家庭预算、城市偏好、专业禁忌。
- 输出要给出明确下一步，但必须标注数据来源和更新时间。

当前可用院校库片段：
{school_context}

上游 zhangxuefeng-skill 参考内容如下，仅作为表达和分析框架，不代表事实数据库：
{skill}
""".strip()


def offline_reply(message: str, profile: dict[str, Any], school_payload: dict[str, Any]) -> str:
    province = profile.get("province") or "你的省份"
    schools = school_payload.get("schools") or []
    examples = "、".join(str(item.get("name")) for item in schools[:4] if isinstance(item, dict))
    return (
        "我先把边界说清楚：本站是非官方张雪峰风格模拟顾问，不是本人，也不能替代省考试院。\n\n"
        "你这个问题现在不能直接拍板。志愿填报至少要先补齐 6 个信息：省份、科类或选科、分数、全省位次、预算、能不能接受的城市和专业。\n\n"
        f"当前本地院校库是演示数据，覆盖样例包括：{examples or '暂无'}。"
        f"你填的省份是 {province}，但没有正式授权数据源和 DeepSeek API Key 时，我不会冒充实时权威库给概率。\n\n"
        f"你刚才的问题是：{message}\n\n"
        "下一步：配置 DEEPSEEK_API_KEY 和 SCHOOL_SOURCE_URL 后，我可以按授权数据源逐项核验学校、专业、城市和风险档。"
    )


def call_deepseek(messages: list[dict[str, str]], profile: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    school_payload = load_school_payload()
    school_context = json.dumps(
        {
            "source": school_payload.get("source"),
            "syncedAt": school_payload.get("syncedAt"),
            "schools": (school_payload.get("schools") or [])[:12],
            "profile": profile,
        },
        ensure_ascii=False,
    )

    if not api_key:
        last_message = messages[-1]["content"] if messages else ""
        return {
            "mode": "offline",
            "model": None,
            "answer": offline_reply(last_message, profile, school_payload),
            "sources": {
                "schoolSource": school_payload.get("source"),
                "syncedAt": school_payload.get("syncedAt"),
            },
        }

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "system", "content": build_system_prompt(school_context)}, *messages],
        "temperature": 0.45,
        "stream": False,
    }
    request = urllib.request.Request(
        DEEPSEEK_ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API 返回 {exc.code}: {detail}") from exc

    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {
        "mode": "deepseek",
        "model": DEEPSEEK_MODEL,
        "answer": answer,
        "usage": data.get("usage"),
        "sources": {
            "schoolSource": school_payload.get("source"),
            "syncedAt": school_payload.get("syncedAt"),
        },
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "MISSINGMrZhang/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            json_response(
                self,
                {
                    "ok": True,
                    "model": DEEPSEEK_MODEL,
                    "hasDeepSeekKey": bool(os.getenv("DEEPSEEK_API_KEY")),
                    "hasSchoolSource": bool(SCHOOL_SOURCE_URL),
                },
            )
            return

        if parsed.path == "/api/schools":
            query = parse_qs(parsed.query)
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
            return

        file_path = STATIC_DIR / "index.html" if parsed.path == "/" else STATIC_DIR / parsed.path.lstrip("/")
        try:
            resolved = file_path.resolve()
            if not str(resolved).startswith(str(STATIC_DIR.resolve())) or not resolved.exists():
                raise FileNotFoundError
            body = resolved.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", MIME_TYPES.get(resolved.suffix, "application/octet-stream"))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            json_response(self, {"error": "Not found"}, 404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/chat":
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
                return

            if parsed.path == "/api/sync/schools":
                if SYNC_TOKEN and self.headers.get("X-Sync-Token") != SYNC_TOKEN:
                    json_response(self, {"error": "同步 token 不正确"}, 403)
                    return
                json_response(self, fetch_authorized_school_source())
                return

            json_response(self, {"error": "Not found"}, 404)
        except Exception as exc:
            json_response(self, {"error": str(exc)}, 400)

    def log_message(self, format: str, *args: Any) -> None:
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))


def main() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8787"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"念张师 (Missing Mr.Zhang) running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
