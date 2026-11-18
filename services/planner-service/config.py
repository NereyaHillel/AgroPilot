from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    """Both URLs are required. A missing one stops startup, naming the variable."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    registry_url: str = Field(min_length=1)
    weather_url: str = Field(min_length=1)
    upstream_timeout_seconds: float = Field(default=10.0, gt=0)

    @field_validator("registry_url", "weather_url")
    @classmethod
    def _drop_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")
