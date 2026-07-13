from pathlib import Path

import pytest

from notion_auto_organizer.organizer import NotionPageOrganizer


class FakeNotion:
    def __init__(self):
        self.archived = False
        self.appended = []

    def get_page_title(self, page_id):
        return "테스트 페이지"

    def list_block_children(self, page_id):
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

    def archive_children(self, page_id):
        self.archived = True

    def append_children(self, page_id, blocks):
        self.appended.extend(blocks)


class FailingAI:
    def organize_markdown(self, markdown):
        raise RuntimeError("AI failed")


class FakeAI:
    def organize_markdown(self, markdown):
        return "# 테스트 페이지\n\n## 핵심 요약\n정리됨"


def test_ai_failure_does_not_replace_notion_page(tmp_path: Path):
    notion = FakeNotion()
    organizer = NotionPageOrganizer(
        notion,
        FailingAI(),
        backups_dir=tmp_path / "backups",
        posts_dir=tmp_path / "posts",
        cache_dir=tmp_path / "cache",
    )

    with pytest.raises(RuntimeError):
        organizer.organize_page("page")

    assert not notion.archived
    assert notion.appended == []
    assert list((tmp_path / "backups").glob("*.md"))


def test_success_backs_up_saves_post_and_replaces_page(tmp_path: Path):
    notion = FakeNotion()
    organizer = NotionPageOrganizer(
        notion,
        FakeAI(),
        backups_dir=tmp_path / "backups",
        posts_dir=tmp_path / "posts",
    )

    result = organizer.organize_page("page")

    assert result.backup_path.exists()
    assert result.post_path.exists()
    assert notion.archived
    assert [block["type"] for block in notion.appended] == ["heading_1", "heading_2", "paragraph"]
