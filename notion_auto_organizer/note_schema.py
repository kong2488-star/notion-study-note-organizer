from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class HeadingBlock(BaseModel):
    type: Literal["heading"] = "heading"
    level: Literal[1, 2, 3]
    text: str


class ParagraphBlock(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    text: str


class BulletedListItemBlock(BaseModel):
    type: Literal["bulleted_list_item"] = "bulleted_list_item"
    text: str


class NumberedListItemBlock(BaseModel):
    type: Literal["numbered_list_item"] = "numbered_list_item"
    text: str


class TodoBlock(BaseModel):
    type: Literal["todo"] = "todo"
    text: str
    checked: bool = False


class QuoteBlock(BaseModel):
    type: Literal["quote"] = "quote"
    text: str


class CodeBlock(BaseModel):
    type: Literal["code"] = "code"
    language: str = ""
    content: str


class DividerBlock(BaseModel):
    type: Literal["divider"] = "divider"


OrganizedBlock = Annotated[
    HeadingBlock
    | ParagraphBlock
    | BulletedListItemBlock
    | NumberedListItemBlock
    | TodoBlock
    | QuoteBlock
    | CodeBlock
    | DividerBlock,
    Field(discriminator="type"),
]


class OrganizedNote(BaseModel):
    blocks: list[OrganizedBlock] = Field(min_length=1)


def render_markdown(note: OrganizedNote) -> str:
    """OrganizedNote를 markdown_to_blocks가 다시 파싱할 수 있는 Markdown 문자열로 변환합니다."""
    lines = [_render_block(block) for block in note.blocks]
    return "\n\n".join(lines) + "\n"


def _render_block(block: OrganizedBlock) -> str:
    if isinstance(block, HeadingBlock):
        return f"{'#' * block.level} {block.text}"
    if isinstance(block, ParagraphBlock):
        return block.text
    if isinstance(block, BulletedListItemBlock):
        return f"- {block.text}"
    if isinstance(block, NumberedListItemBlock):
        return f"1. {block.text}"
    if isinstance(block, TodoBlock):
        checked = "x" if block.checked else " "
        return f"- [{checked}] {block.text}"
    if isinstance(block, QuoteBlock):
        return f"> {block.text}"
    if isinstance(block, CodeBlock):
        return f"```{block.language}\n{block.content}\n```"
    return "---"
