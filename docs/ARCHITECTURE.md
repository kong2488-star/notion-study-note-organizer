# Architecture

## Purpose

This project reads rough developer study notes from a Notion page, converts the block tree into Markdown, organizes the content into a beginner-friendly Korean study document through a selected AI provider, and then replaces the page contents with the organized result.

## Data Flow

```text
Notion page
  -> NotionClient: load block tree
  -> blocks_to_markdown: convert original content to Markdown
  -> backups/: save original Markdown
  -> AIClient: call the selected LangChain agent
  -> posts/: save organized result
  -> markdown_to_blocks: convert organized Markdown back to Notion blocks
  -> NotionClient: archive existing children and append new blocks
```

If the AI call or Markdown organization step fails, the archive step is not performed, so the existing Notion page content remains untouched.

## Module Boundaries

- `notion.py`: handles Notion API requests, block tree loading, archiving, and append chunking.
- `markdown_convert.py`: handles conversion between Notion blocks and Markdown.
- `organizer.py`: coordinates backups, AI calls, output storage, and page replacement.
- `ai_client.py`: defines the shared `AIClient` protocol, prompt, and agent output extraction.
- `gemini_client.py`: implements the LangChain Gemini chat model and agent.
- `openai_client.py`: implements the OpenAI-compatible proxy LangChain chat model and agent.
- `ai_factory.py`: selects the provider implementation based on `AI_PROVIDER`.
- `config.py`: loads `.env` values and validates provider-specific settings.

When adding a new provider, implement `AIClient.organize_markdown()` and keep the provider-specific client logic isolated inside that provider module. The `NotionPageOrganizer` should remain independent of the selected AI provider.
