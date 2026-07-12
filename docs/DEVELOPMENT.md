# Development

## Setup

```powershell
python -m pip install -e ".[dev]"
```

Python 3.10 or later is required. LangChain provider dependencies are defined in `pyproject.toml`.

## Tests

Run all tests:

```powershell
python -m pytest
```

The test suite mocks provider requests and verifies provider selection, agent output extraction, Markdown conversion, Notion chunking, and failure safety when AI organization fails.

Because live API calls are not covered by unit tests, always verify a short prompt before running the full workflow.

## Run

```powershell
python -m notion_auto_organize --page-id "<PAGE_ID>"
```

During execution, the original content is backed up, AI organization runs, and the Notion page is replaced only after the organized result succeeds. Original Markdown is saved under `backups/`, and the AI-generated result is saved under `posts/`.

## Safety Rules

- Do not commit `.env` files, tokens, or keys.
- Run the first attempt on a test Notion page.
- If the AI call fails, do not replace the existing Notion page.
- Keep backup and output files out of source control.
- When changing provider implementations, update the provider client and the related config/factory tests together.
