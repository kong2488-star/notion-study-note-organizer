from notion_auto_organizer.markdown_convert import markdown_to_blocks
from notion_auto_organizer.note_schema import (
    BulletedListItemBlock,
    CodeBlock,
    DividerBlock,
    HeadingBlock,
    NumberedListItemBlock,
    OrganizedNote,
    ParagraphBlock,
    QuoteBlock,
    TodoBlock,
    render_markdown,
)


def test_render_markdown_single_heading():
    note = OrganizedNote(blocks=[HeadingBlock(level=3, text="소제목")])

    assert render_markdown(note) == "### 소제목\n"


def test_render_markdown_consecutive_paragraphs_stay_separate_blocks():
    note = OrganizedNote(
        blocks=[
            ParagraphBlock(text="첫 문단"),
            ParagraphBlock(text="둘째 문단"),
        ]
    )

    blocks = markdown_to_blocks(render_markdown(note))

    assert len(blocks) == 2
    assert all(block["type"] == "paragraph" for block in blocks)


def test_render_markdown_round_trips_every_block_type_through_markdown_to_blocks():
    note = OrganizedNote(
        blocks=[
            HeadingBlock(level=1, text="제목"),
            ParagraphBlock(text="설명 문단"),
            BulletedListItemBlock(text="불릿 항목"),
            NumberedListItemBlock(text="순서 항목"),
            TodoBlock(text="할 일", checked=True),
            QuoteBlock(text="인용문"),
            CodeBlock(language="python", content="x = 1"),
            DividerBlock(),
        ]
    )

    blocks = markdown_to_blocks(render_markdown(note))
    types = [block["type"] for block in blocks]

    assert types == [
        "heading_1",
        "paragraph",
        "bulleted_list_item",
        "numbered_list_item",
        "to_do",
        "quote",
        "code",
        "divider",
    ]
    assert blocks[4]["to_do"]["checked"] is True
    assert blocks[6]["code"]["language"] == "python"
