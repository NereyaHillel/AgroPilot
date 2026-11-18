import pytest
from pydantic import ValidationError

from config import Settings

URLS = {"REGISTRY_URL": "http://registry:8000/", "WEATHER_URL": "http://weather:8001"}


def load(monkeypatch, **overrides):
    for name in ("REGISTRY_URL", "WEATHER_URL", "UPSTREAM_TIMEOUT_SECONDS"):
        monkeypatch.delenv(name, raising=False)
    for name, value in {**URLS, **overrides}.items():
        if value is not None:
            monkeypatch.setenv(name, value)
    return Settings(_env_file=None)


def test_loads_urls_and_default_timeout(monkeypatch):
    settings = load(monkeypatch)
    assert settings.registry_url == "http://registry:8000"  # trailing slash dropped
    assert settings.weather_url == "http://weather:8001"
    assert settings.upstream_timeout_seconds == 10.0


@pytest.mark.parametrize("name", ["REGISTRY_URL", "WEATHER_URL"])
def test_missing_url_stops_startup_naming_it(monkeypatch, name):
    with pytest.raises(ValidationError, match=name.lower()):
        load(monkeypatch, **{name: None})


@pytest.mark.parametrize("value", ["0", "-1", "soon"])
def test_bad_timeout_is_rejected(monkeypatch, value):
    with pytest.raises(ValidationError, match="upstream_timeout_seconds"):
        load(monkeypatch, UPSTREAM_TIMEOUT_SECONDS=value)
