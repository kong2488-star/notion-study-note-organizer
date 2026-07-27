from __future__ import annotations

import json
from typing import Any

import requests

from .exceptions import HttpError

_session = requests.Session()


def request_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    query: dict[str, Any] | None = None,
) -> dict[str, Any]:
    params = {k: v for k, v in query.items() if v is not None} if query else None

    try:
        resp = _session.request(
            method.upper(),
            url,
            headers=headers,
            json=body,
            params=params,
            timeout=60,
        )
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise HttpError(
            f"{method.upper()} {url} failed: HTTP {exc.response.status_code} {exc.response.text}"
        ) from exc
    except requests.ConnectionError as exc:
        raise HttpError(f"{method.upper()} {url} failed: {exc}") from exc

    return resp.json() if resp.text else {}
