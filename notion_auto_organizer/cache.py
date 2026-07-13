from __future__ import annotations

import hashlib
import re
from pathlib import Path


class AIResponseCache:
    def __init__(self, directory: Path, namespace: str = "default") -> None:
        self.directory = directory
        self.namespace = namespace

    def get(self, source_markdown: str) -> str | None:
        path = self._path_for(source_markdown)
        try:
            if not path.exists():
                return None
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return None

    def set(self, source_markdown: str, organized_markdown: str) -> None:
        path = self._path_for(source_markdown)
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            path.write_text(organized_markdown, encoding="utf-8")
        except OSError:
            # Caching is an optimization and must not break page organization.
            return

    def clear(self) -> None:
        try:
            for path in self.directory.glob(f"{self._safe_namespace()}-*.md"):
                path.unlink()
        except OSError:
            return

    def _path_for(self, source_markdown: str) -> Path:
        cache_key = hashlib.sha256(
            f"{self.namespace}\0{source_markdown}".encode("utf-8")
        ).hexdigest()
        return self.directory / f"{self._safe_namespace()}-{cache_key}.md"

    def _safe_namespace(self) -> str:
        return re.sub(r"[^A-Za-z0-9_.-]+", "-", self.namespace)
