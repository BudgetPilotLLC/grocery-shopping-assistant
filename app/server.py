from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import socket
from urllib.parse import parse_qs, urlparse

from .pricing import DEFAULT_STORES, analyze_note, load_catalog


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"
DATA_ROOT = ROOT / "data"
CATALOG_PATH = DATA_ROOT / "catalog.csv"
DEFAULT_LIST_PATH = DATA_ROOT / "grocery-list.txt"
LEGACY_NOTE_PATH = DATA_ROOT / "apple_note.txt"


class GroceryHandler(BaseHTTPRequestHandler):
    server_version = "GroceryAssistant/0.1"

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.add_default_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self.write_json(self.state_payload())
            return
        if parsed.path == "/api/latest-note":
            self.write_json({"text": read_list(), "source": source_payload()})
            return
        if parsed.path == "/api/latest-list":
            self.write_json({"text": read_list(), "source": source_payload()})
            return
        if parsed.path.startswith("/api/"):
            self.write_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        self.serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/analyze":
            payload = self.read_payload()
            text = str(payload.get("text", ""))
            stores = payload.get("stores") or DEFAULT_STORES
            zip_code = str(payload.get("zip", ""))
            self.write_json(self.analysis_payload(text, stores, zip_code))
            return

        if parsed.path == "/api/apple-note":
            if not self.valid_token():
                self.write_json({"error": "Missing or invalid token"}, HTTPStatus.UNAUTHORIZED)
                return
            payload = self.read_payload(allow_raw_text=True)
            text = str(payload.get("text", ""))
            write_list(text)
            stores = payload.get("stores") or DEFAULT_STORES
            zip_code = str(payload.get("zip", ""))
            self.write_json({"saved": True, **self.analysis_payload(text, stores, zip_code)})
            return

        self.write_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def state_payload(self) -> dict:
        note = read_list()
        return {
            "note": note,
            "analysis": self.analysis_payload(note, DEFAULT_STORES, ""),
            "catalog": catalog_payload(),
            "settings": {
                "stores": DEFAULT_STORES,
                "endpoint": "/api/apple-note",
                "token_required": bool(self.server.token),
                "source": source_payload(),
            },
        }

    def analysis_payload(self, text: str, stores: list[str], zip_code: str) -> dict:
        catalog = load_catalog(CATALOG_PATH)
        return analyze_note(text, catalog, stores=stores, zip_code=zip_code)

    def read_payload(self, allow_raw_text: bool = False) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else b""
        content_type = self.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                return json.loads(body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                return {}
        if "application/x-www-form-urlencoded" in content_type:
            parsed = parse_qs(body.decode("utf-8"))
            return {key: values[-1] for key, values in parsed.items()}
        if allow_raw_text:
            return {"text": body.decode("utf-8")}
        return {}

    def valid_token(self) -> bool:
        token = self.server.token
        if not token:
            return True
        supplied = self.headers.get("X-Grocery-Token") or self.headers.get("Authorization", "").removeprefix("Bearer ")
        return supplied == token

    def serve_static(self, request_path: str) -> None:
        relative = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        target = (WEB_ROOT / relative).resolve()
        if WEB_ROOT.resolve() not in target.parents and target != WEB_ROOT.resolve():
            self.write_json({"error": "Invalid path"}, HTTPStatus.BAD_REQUEST)
            return
        if not target.exists() or not target.is_file():
            self.write_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.add_default_headers(content_type)
        self.end_headers()
        self.wfile.write(target.read_bytes())

    def write_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.add_default_headers("application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def add_default_headers(self, content_type: str | None = None) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Grocery-Token, Authorization")
        if content_type:
            self.send_header("Content-Type", content_type)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")


class GroceryServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], handler_class, token: str = ""):
        super().__init__(server_address, handler_class)
        self.token = token


def configured_list_path() -> Path:
    raw_path = os.environ.get("GROCERY_LIST_PATH")
    if not raw_path:
        return DEFAULT_LIST_PATH
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path


def read_list() -> str:
    list_path = configured_list_path()
    if list_path.exists():
        return list_path.read_text(encoding="utf-8")
    if LEGACY_NOTE_PATH.exists():
        return LEGACY_NOTE_PATH.read_text(encoding="utf-8")
    return ""


def write_list(text: str) -> None:
    list_path = configured_list_path()
    list_path.parent.mkdir(parents=True, exist_ok=True)
    list_path.write_text(text, encoding="utf-8")


def source_payload() -> dict:
    list_path = configured_list_path()
    return {
        "path": str(list_path),
        "exists": list_path.exists(),
        "mode": "onedrive-file" if "OneDrive" in str(list_path) else "local-file",
    }


def catalog_payload() -> dict:
    offers = load_catalog(CATALOG_PATH)
    stores = sorted({offer.store for offer in offers})
    return {
        "path": str(CATALOG_PATH),
        "rows": len(offers),
        "stores": stores,
    }


def local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Grocery Shopping Assistant")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8787, type=int)
    parser.add_argument("--token", default=os.environ.get("GROCERY_ASSISTANT_TOKEN", ""))
    args = parser.parse_args()

    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    server = GroceryServer((args.host, args.port), GroceryHandler, token=args.token)
    display_host = "127.0.0.1" if args.host in {"0.0.0.0", ""} else args.host
    print(f"Grocery Shopping Assistant: http://{display_host}:{args.port}")
    if args.host == "0.0.0.0":
        print(f"LAN URL: http://{local_ip()}:{args.port}")
        print(f"Apple Note webhook: http://{local_ip()}:{args.port}/api/apple-note")
    else:
        print(f"Apple Note webhook: http://{display_host}:{args.port}/api/apple-note")
    if args.token:
        print("Apple Note webhook token: required via X-Grocery-Token header")
    print(f"Grocery list file: {configured_list_path()}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
