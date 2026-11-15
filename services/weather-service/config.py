from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    """Every variable is required except the API key. A missing one stops startup."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    provider_base_url: str = Field(min_length=1)
    provider_api_key: str = ""
    provider_timeout_seconds: float = Field(gt=0)
    provider_retries: int = Field(ge=0)
    provider_retry_pause_seconds: float = Field(ge=0)
    fresh_seconds: float = Field(gt=0)
    max_stale_seconds: float = Field(gt=0)

    @field_validator("provider_base_url")
    @classmethod
    def _drop_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    @model_validator(mode="after")
    def _stale_limit_covers_freshness(self) -> "Settings":
        if self.max_stale_seconds < self.fresh_seconds:
            raise ValueError("MAX_STALE_SECONDS must not be shorter than FRESH_SECONDS")
        return self
