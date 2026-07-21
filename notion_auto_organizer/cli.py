from __future__ import annotations

import argparse

from .ai import create_ai_client
from .config import load_settings
from .notion import NotionClient
from .organizer import NotionPageOrganizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Organize a messy Notion developer study page into structured learning-note Markdown."
        ),
    )
    parser.add_argument(
        "page_id",
        help="Notion page ID or page URL to read and replace.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Ignore the cached AI response and organize the current page again.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
        organizer = NotionPageOrganizer(
            NotionClient(settings.notion_token.get_secret_value()),
            create_ai_client(settings),
            cache_namespace=settings.cache_namespace,
        )
        if args.refresh:
            organizer.ai_cache.clear()
        result = organizer.organize_page(args.page_id)
    except Exception as exc:
        parser.exit(1, f"error: {exc}\n")

    print(f"Organized Notion page: {result.title}")
    print(f"Backup saved: {result.backup_path}")
    print(f"Post saved: {result.post_path}")
    print(f"Blocks appended: {result.block_count}")
    return 0
