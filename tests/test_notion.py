import pytest

from notion_auto_organizer import notion as notion_module
from notion_auto_organizer.notion import NotionClient, normalize_page_id

PAGE_ID = "3969cc0317cf8024b936dc7874b3ccf3"


def test_append_children_chunks_at_100(monkeypatch):
    calls = []

    def fake_request_json(method, url, *, headers=None, body=None, query=None):
        calls.append(body["children"])
        return {}

    monkeypatch.setattr(notion_module, "request_json", fake_request_json)
    client = NotionClient("token")
    blocks = [{"object": "block", "type": "divider", "divider": {}} for _ in range(205)]

    client.append_children(PAGE_ID, blocks)

    assert [len(chunk) for chunk in calls] == [100, 100, 5]


def test_list_block_children_follows_pagination(monkeypatch):
    pages = [
        {"results": [{"id": "b1"}], "has_more": True, "next_cursor": "cursor-2"},
        {"results": [{"id": "b2"}], "has_more": False},
    ]
    seen_cursors = []

    def fake_request_json(method, url, *, headers=None, body=None, query=None):
        seen_cursors.append(query["start_cursor"])
        return pages.pop(0)

    monkeypatch.setattr(notion_module, "request_json", fake_request_json)
    client = NotionClient("token")

    children = client.list_block_children(PAGE_ID)

    assert [child["id"] for child in children] == ["b1", "b2"]
    assert seen_cursors == [None, "cursor-2"]


def test_get_page_title_reads_title_property(monkeypatch):
    def fake_request_json(method, url, *, headers=None, body=None, query=None):
        return {
            "properties": {
                "Name": {
                    "type": "title",
                    "title": [{"plain_text": "파이썬 "}, {"plain_text": "정리"}],
                }
            }
        }

    monkeypatch.setattr(notion_module, "request_json", fake_request_json)

    assert NotionClient("token").get_page_title(PAGE_ID) == "파이썬 정리"


def test_get_page_title_falls_back_to_page_id(monkeypatch):
    monkeypatch.setattr(
        notion_module,
        "request_json",
        lambda method, url, *, headers=None, body=None, query=None: {"properties": {}},
    )

    assert NotionClient("token").get_page_title(PAGE_ID) == PAGE_ID


@pytest.mark.parametrize(
    ("raw_page_id", "expected"),
    [
        (PAGE_ID, PAGE_ID),
        (
            "3969cc03-17cf-8024-b936-dc7874b3ccf3",
            "3969cc03-17cf-8024-b936-dc7874b3ccf3",
        ),
        (
            f"https://www.notion.so/p/2-Pydantic-{PAGE_ID}",
            PAGE_ID,
        ),
        (
            f"https://www.notion.so/My-Page-{PAGE_ID}?v=123",
            PAGE_ID,
        ),
    ],
)
def test_normalize_page_id(raw_page_id, expected):
    assert normalize_page_id(raw_page_id) == expected


@pytest.mark.parametrize("invalid", ["not-a-page-id", "", "   "])
def test_normalize_page_id_rejects_invalid_values(invalid):
    with pytest.raises(ValueError):
        normalize_page_id(invalid)
