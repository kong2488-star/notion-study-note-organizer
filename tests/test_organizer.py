from pathlib import Path

import pytest

from notion_auto_organizer.exceptions import AIClientError, NotionError, OrganizationError
from notion_auto_organizer.organizer import NotionPageOrganizer, slugify

PAGE_ID = "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d"
PAGE_URL = f"https://www.notion.so/workspace/테스트-페이지-{PAGE_ID}?pvs=4"


class FakeNotion:
    def __init__(self):
        self.archived = False
        self.appended = []
        self.seen_page_ids = []

    def get_page_title(self, page_id):
        self.seen_page_ids.append(page_id)
        return "테스트 페이지"

    def list_block_children(self, page_id):
        self.seen_page_ids.append(page_id)
        return [
            {
                "id": "block-1",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"plain_text": "대충 적은 개발 메모"}]},
                "has_children": False,
            }
        ]

    def list_block_children_tree(self, page_id):
        return self.list_block_children(page_id)

    def archive_blocks(self, block_ids):
        self.archived = True

    def append_children(self, page_id, blocks):
        self.seen_page_ids.append(page_id)
        self.appended.extend(blocks)


class FailingAppendNotion(FakeNotion):
    def append_children(self, page_id, blocks):
        raise RuntimeError("append failed")


class EmptyNotion(FakeNotion):
    def list_block_children_tree(self, page_id):
        return []


class FailingAI:
    def organize_markdown(self, markdown):
        raise RuntimeError("AI failed")


class FakeAI:
    def organize_markdown(self, markdown):
        return "# 테스트 페이지\n\n## 핵심 요약\n정리됨"


def make_organizer(notion, ai, tmp_path: Path) -> NotionPageOrganizer:
    return NotionPageOrganizer(
        notion,
        ai,
        backups_dir=tmp_path / "backups",
        posts_dir=tmp_path / "posts",
        cache_dir=tmp_path / "cache",
    )


def test_ai_failure_does_not_replace_notion_page(tmp_path: Path):
    notion = FakeNotion()
    organizer = make_organizer(notion, FailingAI(), tmp_path)

    with pytest.raises(AIClientError):
        organizer.organize_page(PAGE_ID)

    assert not notion.archived
    assert notion.appended == []
    assert list((tmp_path / "backups").glob("*.md"))


def test_success_backs_up_saves_post_and_replaces_page(tmp_path: Path):
    notion = FakeNotion()
    organizer = make_organizer(notion, FakeAI(), tmp_path)

    result = organizer.organize_page(PAGE_ID)

    assert result.backup_path.exists()
    assert result.post_path.exists()
    assert notion.archived
    assert [block["type"] for block in notion.appended] == ["heading_1", "heading_2", "paragraph"]


def test_page_url_is_normalized_before_all_notion_calls(tmp_path: Path):
    notion = FakeNotion()
    organizer = make_organizer(notion, FakeAI(), tmp_path)

    organizer.organize_page(PAGE_URL)

    assert notion.seen_page_ids
    assert all(page_id == PAGE_ID for page_id in notion.seen_page_ids)


def test_invalid_page_id_is_rejected_before_any_notion_call(tmp_path: Path):
    notion = FakeNotion()
    organizer = make_organizer(notion, FakeAI(), tmp_path)

    with pytest.raises(ValueError):
        organizer.organize_page("not-a-page-id")

    assert notion.seen_page_ids == []


def test_append_failure_leaves_page_intact(tmp_path: Path):
    notion = FailingAppendNotion()
    organizer = make_organizer(notion, FakeAI(), tmp_path)

    with pytest.raises(NotionError):
        organizer.organize_page(PAGE_ID)

    assert not notion.archived


def test_empty_page_raises_before_ai_or_notion_write(tmp_path: Path):
    notion = EmptyNotion()
    organizer = make_organizer(notion, FakeAI(), tmp_path)

    with pytest.raises(OrganizationError):
        organizer.organize_page(PAGE_ID)

    assert not notion.archived
    assert notion.appended == []


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("파이썬 기초 정리", "파이썬-기초-정리"),
        ("Hello, World! (draft)", "Hello-World-draft"),
        ("  !!@@##  ", "notion-page"),
        ("", "notion-page"),
    ],
)
def test_slugify(value, expected):
    assert slugify(value) == expected
