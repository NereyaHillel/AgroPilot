import pytest
from pydantic import ValidationError

from config import Settings

GOOD = dict(
    PROVIDER_BASE_URL="https://api.open-meteo.com",
    PROVIDER_TIMEOUT_SECONDS="5",
    PROVIDER_RETRIES="2",
    PROVIDER_RETRY_PAUSE_SECONDS="0.5",
    FRESH_SECONDS="10800",
    MAX_STALE_SECONDS="86400",
)


def load(monkeypatch, **overrides):
    for name in list(GOOD) + ["PROVIDER_API_KEY"]:
        monkeypatch.delenv(name, raising=False)
    for name, value in {**GOOD, **overrides}.items():
        if value is not None:
            monkeypatch.setenv(name, value)
    return Settings(_env_file=None)


def test_loads_from_the_environment(monkeypatch):
    settings = load(monkeypatch)
    assert settings.provider_base_url == "https://api.open-meteo.com"
    assert settings.provider_retries == 2
    assert settings.fresh_seconds == 10800
    assert settings.max_stale_seconds == 86400
    assert settings.provider_api_key == ""  # may be empty


@pytest.mark.parametrize("name", list(GOOD))
def test_every_required_variable_stops_startup(monkeypatch, name):
    with pytest.raises(ValidationError, match=name.lower()):
        load(monkeypatch, **{name: None})


@pytest.mark.parametrize(
    "overrides",
    [
        {"PROVIDER_TIMEOUT_SECONDS": "0"},
        {"PROVIDER_RETRIES": "-1"},
        {"PROVIDER_RETRY_PAUSE_SECONDS": "-1"},
        {"FRESH_SECONDS": "0"},
        {"MAX_STALE_SECONDS": "60"},  # shorter than FRESH_SECONDS
        {"PROVIDER_BASE_URL": ""},
    ],
)
def test_bad_values_are_rejected(monkeypatch, overrides):
    with pytest.raises(ValidationError):
        load(monkeypatch, **overrides)


def test_base_url_trailing_slash_is_dropped(monkeypatch):
    assert load(monkeypatch, PROVIDER_BASE_URL="http://x/").provider_base_url == "http://x"
