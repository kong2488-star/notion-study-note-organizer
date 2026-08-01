from notion_auto_organizer.markdown_convert import (
    blocks_to_markdown,
    markdown_to_blocks,
    normalize_code_language,
)


def test_blocks_to_markdown_basic_blocks():
    blocks = [
        {
            "type": "heading_1",
            "heading_1": {"rich_text": [{"plain_text": "JavaScript Scope"}]},
            "has_children": False,
        },
        {
            "type": "paragraph",
            "paragraph": {"rich_text": [{"plain_text": "스코프는 변수 접근 범위다."}]},
            "has_children": False,
        },
        {
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"plain_text": "전역 스코프"}]},
            "has_children": False,
        },
        {
            "type": "code",
            "code": {"language": "javascript", "rich_text": [{"plain_text": "const x = 1;"}]},
            "has_children": False,
        },
    ]

    markdown = blocks_to_markdown(blocks)

    assert "# JavaScript Scope" in markdown
    assert "스코프는 변수 접근 범위다." in markdown
    assert "- 전역 스코프" in markdown
    assert "```javascript\nconst x = 1;\n```" in markdown


def test_markdown_to_blocks_basic_blocks():
    markdown = """# 제목

## 핵심 요약
- 하나
1. 둘
- [x] 체크

> 인용

```js
const value = 1;
```
---
"""

    blocks = markdown_to_blocks(markdown)
    types = [block["type"] for block in blocks]

    assert types == [
        "heading_1",
        "heading_2",
        "bulleted_list_item",
        "numbered_list_item",
        "to_do",
        "quote",
        "code",
        "divider",
    ]
    assert blocks[6]["code"]["language"] == "javascript"


def test_normalize_code_language_maps_text_to_plain_text():
    assert normalize_code_language("text") == "plain text"


def test_markdown_to_blocks_splits_long_paragraph():
    markdown = "a" * 3900

    blocks = markdown_to_blocks(markdown)

    assert len(blocks) == 3
    assert all(block["type"] == "paragraph" for block in blocks)
