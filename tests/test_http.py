import io
import json
from urllib.error import HTTPError, URLError

import pytest

from notion_auto_organizer import http as http_module
from notion_auto_organizer.http import HttpError, request_json


class FakeResponse:
    def __init__(self, raw: bytes) -> None:
        self._raw = raw

    def read(self) -> bytes:
        return self._raw

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args) -> None:
        return None


def test_request_json_encodes_query_and_drops_none(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        return FakeResponse(b'{"ok": true}')

    monkeypatch.setattr(http_module, "urlopen", fake_urlopen)

    result = request_json(
        "get",
        "https://api.example.com/v1/items",
        query={"page_size": 100, "start_cursor": None},
    )

    assert result == {"ok": True}
    assert captured["url"] == "https://api.example.com/v1/items?page_size=100"
    assert captured["method"] == "GET"


def test_request_json_sends_json_body_with_content_type(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["data"] = req.data
        captured["content_type"] = req.get_header("Content-type")
        return FakeResponse(b"")

    monkeypatch.setattr(http_module, "urlopen", fake_urlopen)

    result = request_json("PATCH", "https://api.example.com/v1/items", body={"archived": True})

    assert result == {}
    assert json.loads(captured["data"].decode("utf-8")) == {"archived": True}
    assert captured["content_type"] == "application/json"


def test_request_json_wraps_http_error_with_response_detail(monkeypatch):
    def fake_urlopen(req, timeout):
        raise HTTPError(
            req.full_url,
            429,
            "Too Many Requests",
            hdrs=None,
            fp=io.BytesIO(b'{"message": "rate limited"}'),
        )

    monkeypatch.setattr(http_module, "urlopen", fake_urlopen)

    with pytest.raises(HttpError, match=r"HTTP 429.*rate limited"):
        request_json("GET", "https://api.example.com/v1/items")


def test_request_json_wraps_url_error(monkeypatch):
    def fake_urlopen(req, timeout):
        raise URLError("connection refused")

    monkeypatch.setattr(http_module, "urlopen", fake_urlopen)

    with pytest.raises(HttpError, match="connection refused"):
        request_json("GET", "https://api.example.com/v1/items")
