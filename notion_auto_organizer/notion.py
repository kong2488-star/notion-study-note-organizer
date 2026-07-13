from __future__ import annotations

import re
from typing import Any

from .http import request_json

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
NOTION_PAGE_ID_PATTERN = re.compile(
    r"(?P<page_id>[0-9a-fA-F]{32}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)


class NotionClient:
    def __init__(self, token: str) -> None:
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
        }

    def retrieve_page(self, page_id: str) -> dict[str, Any]:
        normalized_page_id = normalize_page_id(page_id)
        return request_json(
            "GET", f"{NOTION_API_BASE}/pages/{normalized_page_id}", headers=self.headers
        )

    def get_page_title(self, page_id: str) -> str:
        page = self.retrieve_page(page_id)
        for prop in page.get("properties", {}).values():
            if prop.get("type") == "title":
                title = "".join(part.get("plain_text", "") for part in prop.get("title", []))
                if title.strip():
                    return title.strip()
        return page_id

    def list_block_children(self, block_id: str) -> list[dict[str, Any]]:
        children: list[dict[str, Any]] = []
        cursor = None
        while True:
            payload = request_json(
                "GET",
                f"{NOTION_API_BASE}/blocks/{block_id}/children",
                headers=self.headers,
                query={"page_size": 100, "start_cursor": cursor},
            )
            children.extend(payload.get("results", []))
            if not payload.get("has_more"):
                return children
            cursor = payload.get("next_cursor")

    def list_block_children_tree(self, block_id: str) -> list[dict[str, Any]]:
        children = self.list_block_children(block_id)
        for child in children:
            if child.get("has_children"):
                child["children"] = self.list_block_children_tree(child["id"])
        return children

    def archive_block(self, block_id: str) -> None:
        request_json(
            "PATCH",
            f"{NOTION_API_BASE}/blocks/{block_id}",
            headers=self.headers,
            body={"archived": True},
        )

    def append_children(self, block_id: str, children: list[dict[str, Any]]) -> None:
        for start in range(0, len(children), 100):
            chunk = children[start : start + 100]
            request_json(
                "PATCH",
                f"{NOTION_API_BASE}/blocks/{block_id}/children",
                headers=self.headers,
                body={"children": chunk},
            )

    def archive_children(self, block_id: str) -> None:
        for child in self.list_block_children(block_id):
            self.archive_block(child["id"])


def normalize_page_id(page_id: str) -> str:
    stripped = page_id.strip()
    if not stripped:
        raise ValueError("page_id cannot be empty.")

    match = NOTION_PAGE_ID_PATTERN.search(stripped)
    if match is None:
        raise ValueError(f"Could not find a valid Notion page ID in: {page_id!r}")
    return match.group("page_id")
