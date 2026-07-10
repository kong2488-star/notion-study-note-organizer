from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class HttpError(RuntimeError):
    pass


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    query: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if query:
        url = f"{url}?{urlencode({k: v for k, v in query.items() if v is not None})}"

    data = None
    request_headers = headers.copy() if headers else {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")

    req = Request(url, data=data, headers=request_headers, method=method.upper())
    try:
        with urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise HttpError(f"{method.upper()} {url} failed: HTTP {exc.code} {detail}") from exc
    except URLError as exc:
        raise HttpError(f"{method.upper()} {url} failed: {exc.reason}") from exc

    if not raw:
        return {}
    return json.loads(raw)
