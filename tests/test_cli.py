from pathlib import Path

import pytest

from notion_auto_organizer import cli
from notion_auto_organizer.config import Settings
from notion_auto_organizer.organizer import OrganizeResult

PAGE_ID = "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d"


def make_settings(**overrides) -> Settings:
    values = {
        "notion_token": "secret-token",
        "ai_provider": "gemini",
        "ai_api_key": "ai-key",
        "ai_model": "test-model",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


class FakeCache:
    def __init__(self) -> None:
        self.cleared = False

    def clear(self) -> None:
        self.cleared = True


class FakeOrganizer:
    instances: list["FakeOrganizer"] = []

    def __init__(self, notion, ai_client, *, cache_namespace) -> None:
        self.cache_namespace = cache_namespace
        self.ai_cache = FakeCache()
        self.organized_page_ids: list[str] = []
        FakeOrganizer.instances.append(self)

    def organize_page(self, page_id: str) -> OrganizeResult:
        self.organized_page_ids.append(page_id)
        return OrganizeResult(
            title="테스트 페이지",
            backup_path=Path("backups/test.md"),
            post_path=Path("posts/test.md"),
            block_count=3,
        )


@pytest.fixture
def patched_cli(monkeypatch):
    FakeOrganizer.instances = []
    monkeypatch.setattr(cli, "load_settings", make_settings)
    monkeypatch.setattr(cli, "create_ai_client", lambda settings: object())
    monkeypatch.setattr(cli, "NotionClient", lambda token: object())
    monkeypatch.setattr(cli, "NotionPageOrganizer", FakeOrganizer)
    return FakeOrganizer


def test_main_success_prints_result(patched_cli, capsys):
    exit_code = cli.main([PAGE_ID])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Organized Notion page: 테스트 페이지" in out
    assert "Blocks appended: 3" in out
    organizer = patched_cli.instances[0]
    assert organizer.organized_page_ids == [PAGE_ID]
    assert not organizer.ai_cache.cleared


def test_main_refresh_clears_cache(patched_cli):
    cli.main([PAGE_ID, "--refresh"])

    assert patched_cli.instances[0].ai_cache.cleared


def test_main_exits_with_error_when_settings_fail(monkeypatch, capsys):
    def failing_settings():
        raise ValueError("Missing required environment values: NOTION_TOKEN")

    monkeypatch.setattr(cli, "load_settings", failing_settings)

    with pytest.raises(SystemExit) as excinfo:
        cli.main([PAGE_ID])

    assert excinfo.value.code == 1
    assert "error: Missing required environment values" in capsys.readouterr().err


def test_page_id_is_required(capsys):
    with pytest.raises(SystemExit):
        cli.main([])

    assert "page_id" in capsys.readouterr().err


def test_settings_namespace_per_provider():
    gemini = make_settings()
    openai = make_settings(ai_provider="openai", ai_model="gpt-test")

    assert gemini.cache_namespace == "gemini-test-model"
    assert openai.cache_namespace == "openai-gpt-test"
