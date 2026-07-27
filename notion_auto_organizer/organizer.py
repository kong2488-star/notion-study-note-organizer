from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .ai import AIClient
from .cache import AIResponseCache
from .exceptions import AIClientError, NotionError, OrganizationError
from .markdown_convert import blocks_to_markdown, markdown_to_blocks
from .notion import NotionClient, normalize_page_id


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
        cache_dir: Path = Path("cache"),
        cache_namespace: str = "default",
    ) -> None:
        self.notion = notion
        self.ai_client = ai_client
        self.backups_dir = backups_dir
        self.posts_dir = posts_dir
        self.ai_cache = AIResponseCache(cache_dir, cache_namespace)

    def organize_page(self, page_id: str) -> OrganizeResult:
        page_id = normalize_page_id(page_id)

        print("Notion 페이지 읽는 중...", flush=True)
        try:
            title = self.notion.get_page_title(page_id)
            blocks = self.notion.list_block_children_tree(page_id)
        except Exception as exc:
            raise NotionError(f"[Notion 읽기] 페이지 조회 실패 ({page_id}): {exc}") from exc

        old_block_ids = [b["id"] for b in blocks]
        original_markdown = blocks_to_markdown(blocks)
        if not original_markdown.strip():
            raise OrganizationError(
                "[페이지 읽기] 정리할 내용이 없습니다. 페이지에 블록을 추가한 뒤 다시 실행하세요."
            )

        safe_title = slugify(title)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.posts_dir.mkdir(parents=True, exist_ok=True)

        try:
            backup_path = self.backups_dir / f"{safe_title}-{timestamp}.md"
            backup_path.write_text(original_markdown, encoding="utf-8")
        except Exception as exc:
            raise OrganizationError(f"[백업 저장] 백업 파일 쓰기 실패: {exc}") from exc

        organized_markdown = self.ai_cache.get(original_markdown)
        if organized_markdown is None:
            print("AI로 내용 정리 중...", flush=True)
            try:
                organized_markdown = self.ai_client.organize_markdown(original_markdown)
            except Exception as exc:
                raise AIClientError(f"[AI 정리] AI 응답 실패: {exc}") from exc
            self.ai_cache.set(original_markdown, organized_markdown)
        else:
            print("캐시된 결과 사용 중.", flush=True)

        try:
            post_path = self.posts_dir / f"{safe_title}-{timestamp}-organized.md"
            post_path.write_text(organized_markdown, encoding="utf-8")
        except Exception as exc:
            raise OrganizationError(f"[결과 저장] 정리 파일 쓰기 실패: {exc}") from exc

        new_blocks = markdown_to_blocks(organized_markdown)

        print(f"새 블록 {len(new_blocks)}개 추가 중...", flush=True)
        try:
            self.notion.append_children(page_id, new_blocks)
        except Exception as exc:
            raise NotionError(f"[Notion 쓰기] 새 블록 추가 실패: {exc}") from exc

        print(f"기존 블록 {len(old_block_ids)}개 보관 중...", flush=True)
        try:
            self.notion.archive_blocks(old_block_ids)
        except Exception as exc:
            raise NotionError(f"[Notion 쓰기] 기존 블록 보관 실패: {exc}") from exc

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
