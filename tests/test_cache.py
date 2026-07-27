from pathlib import Path

from notion_auto_organizer.cache import AIResponseCache
from notion_auto_organizer.organizer import NotionPageOrganizer

PAGE_ID = "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d"


class FakeNotion:
    def __init__(self) -> None:
        self.archived = False
        self.appended = []

    def get_page_title(self, page_id: str) -> str:
        return "Cache test"

    def list_block_children_tree(self, page_id: str) -> list[dict]:
        return [
            {
                "id": "block-1",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"plain_text": "rough note"}]},
                "has_children": False,
            }
        ]

    def archive_blocks(self, block_ids: list[str]) -> None:
        self.archived = True

    def append_children(self, page_id: str, blocks: list[dict]) -> None:
        self.appended.extend(blocks)


class CountingAI:
    def __init__(self) -> None:
        self.calls = 0

    def organize_markdown(self, markdown: str) -> str:
        self.calls += 1
        return "# Organized\n\nA cached result."


def test_cache_hit_returns_saved_response(tmp_path: Path) -> None:
    cache = AIResponseCache(tmp_path / "cache", namespace="gemini-test")
    cache.set("source", "organized")

    assert cache.get("source") == "organized"
    assert cache.get("different source") is None


def test_same_source_uses_cached_ai_response(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    first_ai = CountingAI()
    first = NotionPageOrganizer(
        FakeNotion(),
        first_ai,
        backups_dir=tmp_path / "backups",
        posts_dir=tmp_path / "posts",
        cache_dir=cache_dir,
        cache_namespace="gemini-test",
    )
    first.organize_page(PAGE_ID)

    second_ai = CountingAI()
    second = NotionPageOrganizer(
        FakeNotion(),
        second_ai,
        backups_dir=tmp_path / "backups",
        posts_dir=tmp_path / "posts",
        cache_dir=cache_dir,
        cache_namespace="gemini-test",
    )
    second.organize_page(PAGE_ID)

    assert first_ai.calls == 1
    assert second_ai.calls == 0
