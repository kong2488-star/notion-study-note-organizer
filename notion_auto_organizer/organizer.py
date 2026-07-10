from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .ai_client import AIClient
from .markdown_convert import blocks_to_markdown, markdown_to_blocks
from .notion import NotionClient


@dataclass(frozen=True)
class OrganizeResult:
    title: str
    backup_path: Path
    post_path: Path
    block_count: int


class NotionPageOrganizer:
    def __init__(
        self,
        notion: NotionClient,
        ai_client: AIClient,
        *,
        backups_dir: Path = Path("backups"),
        posts_dir: Path = Path("posts"),
    ) -> None:
        self.notion = notion
        self.ai_client = ai_client
        self.backups_dir = backups_dir
        self.posts_dir = posts_dir

    def organize_page(self, page_id: str) -> OrganizeResult:
        title = self.notion.get_page_title(page_id)
        blocks = self.notion.list_block_children_tree(page_id)
        original_markdown = blocks_to_markdown(blocks)

        safe_title = slugify(title)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.posts_dir.mkdir(parents=True, exist_ok=True)

        backup_path = self.backups_dir / f"{safe_title}-{timestamp}.md"
        backup_path.write_text(original_markdown, encoding="utf-8")

        organized_markdown = self.ai_client.organize_markdown(original_markdown)
        post_path = self.posts_dir / f"{safe_title}-organized.md"
        post_path.write_text(organized_markdown, encoding="utf-8")

        new_blocks = markdown_to_blocks(organized_markdown)
        self.notion.archive_children(page_id)
        self.notion.append_children(page_id, new_blocks)

        return OrganizeResult(
            title=title,
            backup_path=backup_path,
            post_path=post_path,
            block_count=len(new_blocks),
        )


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^\w가-힣.-]+", "-", value.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-_.")
    return cleaned or "notion-page"
