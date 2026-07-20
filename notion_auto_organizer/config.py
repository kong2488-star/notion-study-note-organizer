from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    notion_token: SecretStr = Field(min_length=1)
    ai_provider: Literal["gemini", "openai"]
    ai_api_key: SecretStr = Field(min_length=1)
    ai_model: str = Field(min_length=1)
    ai_base_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        str_strip_whitespace=True,
    )

    @field_validator("notion_token", "ai_api_key")
    @classmethod
    def validate_secret(cls, value: SecretStr) -> SecretStr:
        stripped = value.get_secret_value().strip()
        if not stripped:
            raise ValueError("must not be empty")
        return SecretStr(stripped)

    @field_validator("ai_base_url", mode="before")
    @classmethod
    def empty_base_url_to_none(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @model_validator(mode="after")
    def validate_provider_settings(self) -> Settings:
        if self.ai_provider == "gemini" and self.ai_base_url is not None:
            raise ValueError("AI_BASE_URL is only supported when AI_PROVIDER=openai")
        return self

    @property
    def cache_namespace(self) -> str:
        return f"{self.ai_provider}-{self.ai_model}"


def load_settings(env_file: Path | None = Path(".env")) -> Settings:
    return Settings(
        _env_file=env_file,
        _env_file_encoding="utf-8",
    )
