from __future__ import annotations


class OrganizationError(Exception):
    """Base error for all page organization failures."""


class NotionError(OrganizationError):
    """Raised when a Notion API call fails."""


class AIClientError(OrganizationError):
    """Raised when the AI provider call fails."""


class HttpError(RuntimeError):
    """Raised when an HTTP request fails at transport level."""
