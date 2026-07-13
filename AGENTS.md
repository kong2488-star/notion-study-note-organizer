# Project Agent Notes

## Purpose

This project reads rough developer study notes from one Notion page, converts the blocks to Markdown, asks a selected AI provider to organize the notes into a beginner-friendly Korean study document, and replaces the page contents with the organized result.

## Workflow

1. Load `.env` settings.
2. Read the target Notion page and its block tree.
3. Convert the original blocks to Markdown.
4. Save the original Markdown under `backups/`.
5. Send the Markdown to the selected AI provider.
6. Save the organized Markdown under `posts/`.
7. Only after the AI result succeeds, archive the existing Notion children and append the new blocks.

If the AI call or organization step fails, do not replace the Notion page.

## Important Files

- `notion_auto_organizer/notion.py`: Notion API client, page ID/URL normalization, block tree loading, archiving, and append chunking.
- `notion_auto_organizer/markdown_convert.py`: Notion block and Markdown conversion.
- `notion_auto_organizer/organizer.py`: Backup, AI organization, output, and page replacement workflow.
- `notion_auto_organizer/ai_client.py`: Shared `AIClient` protocol, prompt, and agent output extraction.
- `notion_auto_organizer/gemini_client.py`: LangChain Gemini provider implementation.
- `notion_auto_organizer/openai_client.py`: LangChain OpenAI-compatible provider implementation.
- `notion_auto_organizer/ai_factory.py`: Provider selection based on `AI_PROVIDER`.
- `notion_auto_organizer/config.py`: `.env` loading and provider-specific configuration validation.

## Documentation

- `docs/ARCHITECTURE.md`: module boundaries and end-to-end data flow.
- `docs/AI_PROVIDERS.md`: Gemini/OpenAI settings and provider contract.
- `docs/DEVELOPMENT.md`: setup, tests, execution, and safety rules.

Read the relevant document before changing architecture, AI providers, or development workflows.

## Provider Selection

Set `AI_PROVIDER` in `.env`:

```env
AI_PROVIDER=gemini
```

For OpenAI-compatible proxy usage:

```env
AI_PROVIDER=openai
PROXY_TOKEN=...
CHAT_PROXY_URL=...
OPENAI_MODEL=...
```

Gemini uses `GEMINI_API_KEY` and `GEMINI_MODEL`. Never commit `.env` or expose API keys in logs, tests, or error messages.

## Commands

Install the project and development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run tests:

```powershell
python -m pytest
```

Organize a test Notion page:

```powershell
python -m notion_auto_organizer --page-id "<PAGE_ID>"
```

Run a short provider prompt before sending a full Notion page. Use a test page first because the successful workflow replaces the page contents.

## Coding Rules

- code style **Python**: Follow PEP8
  - Use **ruff format** (Black-compatible) for consistent style; run `ruff check` for linting
  - Always include **type hints**
- New AI providers must implement `AIClient.organize_markdown()`.
- Keep provider-specific SDK code inside its provider client.
- Keep `NotionPageOrganizer` independent of the selected AI provider.
- Preserve the backup-before-replacement workflow.
- Keep generated `backups/` and `posts/` files out of source control.
- Add or update unit tests for provider selection, response extraction, Markdown conversion, and failure safety.
- Do not add automatic retries or new external tools without documenting the behavior and testing the failure path.
