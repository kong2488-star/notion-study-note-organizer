from __future__ import annotations

import re
from typing import Any


SUPPORTED_CHILD_TYPES = {
    "paragraph",
    "bulleted_list_item",
    "numbered_list_item",
    "to_do",
    "toggle",
    "quote",
    "callout",
}


def blocks_to_markdown(blocks: list[dict[str, Any]], depth: int = 0) -> str:
    lines: list[str] = []
    for block in blocks:
        block_type = block.get("type")
        data = block.get(block_type, {}) if block_type else {}
        indent = "  " * depth

        if block_type == "paragraph":
            lines.append(f"{indent}{rich_text_to_markdown(data.get('rich_text', []))}".rstrip())
        elif block_type == "heading_1":
            lines.append(f"# {rich_text_to_markdown(data.get('rich_text', []))}")
        elif block_type == "heading_2":
            lines.append(f"## {rich_text_to_markdown(data.get('rich_text', []))}")
        elif block_type == "heading_3":
            lines.append(f"### {rich_text_to_markdown(data.get('rich_text', []))}")
        elif block_type == "bulleted_list_item":
            lines.append(f"{indent}- {rich_text_to_markdown(data.get('rich_text', []))}")
        elif block_type == "numbered_list_item":
            lines.append(f"{indent}1. {rich_text_to_markdown(data.get('rich_text', []))}")
        elif block_type == "to_do":
            checked = "x" if data.get("checked") else " "
            lines.append(f"{indent}- [{checked}] {rich_text_to_markdown(data.get('rich_text', []))}")
        elif block_type == "quote":
            lines.append(f"> {rich_text_to_markdown(data.get('rich_text', []))}")
        elif block_type == "code":
            language = data.get("language", "")
            lines.append(f"```{language}".rstrip())
            lines.append(rich_text_to_plain(data.get("rich_text", [])))
            lines.append("```")
        elif block_type == "divider":
            lines.append("---")
        elif block_type in {"image", "file", "pdf", "video"}:
            lines.append(file_block_to_markdown(block_type, data))
        elif block_type in {"toggle", "callout"}:
            label = rich_text_to_markdown(data.get("rich_text", []))
            prefix = "Toggle" if block_type == "toggle" else "Callout"
            lines.append(f"{indent}> [{prefix}] {label}".rstrip())
        elif block_type == "bookmark":
            caption = rich_text_to_plain(data.get("caption", []))
            url = data.get("url", "")
            lines.append(f"[{caption or url}]({url})" if url else caption)
        elif block_type == "unsupported":
            lines.append("> Unsupported Notion block was omitted.")

        if block.get("has_children") and block_type in SUPPORTED_CHILD_TYPES:
            child_md = blocks_to_markdown(block.get("children", []), depth + 1)
            if child_md:
                lines.append(child_md)

        lines.append("")

    return "\n".join(lines).strip() + ("\n" if lines else "")


def rich_text_to_plain(parts: list[dict[str, Any]]) -> str:
    return "".join(part.get("plain_text", "") for part in parts)


def rich_text_to_markdown(parts: list[dict[str, Any]]) -> str:
    output: list[str] = []
    for part in parts:
        text = part.get("plain_text", "")
        annotations = part.get("annotations", {})
        if annotations.get("code"):
            text = f"`{text}`"
        if annotations.get("bold"):
            text = f"**{text}**"
        if annotations.get("italic"):
            text = f"*{text}*"
        if annotations.get("strikethrough"):
            text = f"~~{text}~~"
        href = part.get("href")
        if href:
            text = f"[{text}]({href})"
        output.append(text)
    return "".join(output)


def file_block_to_markdown(block_type: str, data: dict[str, Any]) -> str:
    source = data.get("external") or data.get("file") or {}
    url = source.get("url", "")
    caption = rich_text_to_plain(data.get("caption", [])) or block_type
    return f"![{caption}]({url})" if block_type == "image" and url else f"[{caption}]({url})"


def markdown_to_blocks(markdown: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    paragraph_lines: list[str] = []
    lines = markdown.splitlines()
    index = 0

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        text = " ".join(line.strip() for line in paragraph_lines if line.strip())
        paragraph_lines = []
        if text:
            blocks.extend(text_to_paragraph_blocks(text))

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            index += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            language = stripped[3:].strip() or "plain text"
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            blocks.append(code_block("\n".join(code_lines), language))
            index += 1
            continue

        heading_match = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading_match:
            flush_paragraph()
            level = len(heading_match.group(1))
            blocks.append(text_block(f"heading_{level}", heading_match.group(2)))
            index += 1
            continue

        if stripped == "---":
            flush_paragraph()
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            index += 1
            continue

        todo_match = re.match(r"^- \[([ xX])\]\s+(.+)$", stripped)
        if todo_match:
            flush_paragraph()
            blocks.append(todo_block(todo_match.group(2), todo_match.group(1).lower() == "x"))
            index += 1
            continue

        bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
        if bullet_match:
            flush_paragraph()
            blocks.append(text_block("bulleted_list_item", bullet_match.group(1)))
            index += 1
            continue

        numbered_match = re.match(r"^\d+\.\s+(.+)$", stripped)
        if numbered_match:
            flush_paragraph()
            blocks.append(text_block("numbered_list_item", numbered_match.group(1)))
            index += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            blocks.append(text_block("quote", stripped.lstrip("> ").strip()))
            index += 1
            continue

        paragraph_lines.append(line)
        index += 1

    flush_paragraph()
    return blocks


def text_to_paragraph_blocks(text: str) -> list[dict[str, Any]]:
    return [text_block("paragraph", chunk) for chunk in split_text(text)]


def text_block(block_type: str, text: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": block_type,
        block_type: {"rich_text": rich_text(text)},
    }


def todo_block(text: str, checked: bool) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {"rich_text": rich_text(text), "checked": checked},
    }


def code_block(text: str, language: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "code",
        "code": {"rich_text": rich_text(text), "language": normalize_code_language(language)},
    }


def rich_text(text: str) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": chunk}} for chunk in split_text(text)]


def split_text(text: str, size: int = 1900) -> list[str]:
    if not text:
        return [""]
    return [text[i : i + size] for i in range(0, len(text), size)]


def normalize_code_language(language: str) -> str:
    normalized = language.strip().lower()
    aliases = {
        "js": "javascript",
        "ts": "typescript",
        "py": "python",
        "shell": "bash",
        "sh": "bash",
        "txt": "plain text",
    }
    return aliases.get(normalized, normalized or "plain text")
