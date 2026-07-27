import json
from unittest.mock import MagicMock

import pytest
import requests

from notion_auto_organizer import http as http_module
from notion_auto_organizer.exceptions import HttpError
from notion_auto_organizer.http import request_json


def _mock_session(monkeypatch, *, text: str, status: int = 200, exc=None):
    mock_resp = MagicMock()
    mock_resp.text = text
    mock_resp.status_code = status
    mock_resp.json.return_value = json.loads(text) if text else {}
    if exc is not None:
        mock_resp.raise_for_status.side_effect = exc
    else:
        mock_resp.raise_for_status.return_value = None

    mock_session = MagicMock()
    mock_session.request.return_value = mock_resp
    monkeypatch.setattr(http_module, "_session", mock_session)
    return mock_session


def test_request_json_encodes_query_and_drops_none(monkeypatch):
    mock_session = _mock_session(monkeypatch, text='{"ok": true}')

    result = request_json(
        "get",
        "https://api.example.com/v1/items",
        query={"page_size": 100, "start_cursor": None},
    )

    assert result == {"ok": True}
    _, kwargs = mock_session.request.call_args
    assert kwargs["params"] == {"page_size": 100}
    assert mock_session.request.call_args[0][0] == "GET"


def test_request_json_sends_json_body_with_content_type(monkeypatch):
    mock_session = _mock_session(monkeypatch, text="")

    result = request_json("PATCH", "https://api.example.com/v1/items", body={"archived": True})

    assert result == {}
    _, kwargs = mock_session.request.call_args
    assert kwargs["json"] == {"archived": True}


def test_request_json_wraps_http_error_with_response_detail(monkeypatch):
    http_exc = requests.HTTPError(
        response=MagicMock(status_code=429, text='{"message": "rate limited"}')
    )
    _mock_session(monkeypatch, text="", status=429, exc=http_exc)

    with pytest.raises(HttpError, match=r"HTTP 429.*rate limited"):
        request_json("GET", "https://api.example.com/v1/items")


def test_request_json_wraps_url_error(monkeypatch):
    mock_session = MagicMock()
    mock_session.request.side_effect = requests.ConnectionError("connection refused")
    monkeypatch.setattr(http_module, "_session", mock_session)

    with pytest.raises(HttpError, match="connection refused"):
        request_json("GET", "https://api.example.com/v1/items")
