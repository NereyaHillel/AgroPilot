from pathlib import Path
from urllib.parse import urlsplit

from pydantic import ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_DIR = Path(__file__).resolve().parent
ENV_FILE = SERVICE_DIR / ".env"
DEFAULT_SQLITE_URL = f"sqlite:///{SERVICE_DIR / 'registry.db'}"
SUPPORTED_SCHEMES = {"sqlite", "postgresql", "postgres"}


class Settings(BaseSettings):
    # A real environment variable wins over .env, even when empty; os.environ is never modified.
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore", hide_input_in_errors=True)

    database_url: str = DEFAULT_SQLITE_URL
    # Optional: without a bucket the photo routes answer 503. Credentials are never read here;
    # boto3 finds them itself.
    aws_s3_bucket: str = ""
    aws_region: str | None = None

    @field_validator("database_url")
    @classmethod
    def _check_url(cls, url: str) -> str:
        if not url:
            raise ValueError("empty DATABASE_URL; unset it to use registry.db")
        # Messages name only the scheme, since the URL may hold a password.
        scheme = urlsplit(url).scheme
        if not scheme:
            raise ValueError("DATABASE_URL has no scheme; expected sqlite:/// or postgresql://")
        if scheme not in SUPPORTED_SCHEMES:
            raise ValueError(f"Unsupported DATABASE_URL scheme: {scheme!r}")
        return url


def database_url(env_file: Path = ENV_FILE) -> str:
    try:
        return Settings(_env_file=env_file).database_url
    except ValidationError as exc:
        # Re-raise with only the validator's message, never the input value.
        raise ValueError("; ".join(e["msg"].removeprefix("Value error, ") for e in exc.errors())) from None


def s3_settings(env_file: Path = ENV_FILE) -> tuple[str, str | None]:
    settings = Settings(_env_file=env_file)
    return settings.aws_s3_bucket, settings.aws_region or None
