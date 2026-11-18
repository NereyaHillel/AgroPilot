"""Fake Open-Meteo behind httpx.MockTransport, a fake clock, and an app wired to both."""

import json
from datetime import UTC, date, datetime, timedelta

import httpx
import pytest
from fastapi.testclient import TestClient

from config import Settings
from main import create_app

START = datetime(2026, 11, 12, 6, 0, tzinfo=UTC)


def provider_body(first=date(2026, 11, 12), count=7, offset=0, et0=None, rain=None):
    et0 = et0 if et0 is not None else [3.1 + i / 10 for i in range(count)]
    rain = rain if rain is not None else [0.0] * count
    return {
        "utc_offset_seconds": offset,
        "daily": {
            "time": [(first + timedelta(days=i)).isoformat() for i in range(count)],
            "et0_fao_evapotranspiration": et0,
            "rain_sum": rain,
        },
    }


class FakeClock:
    def __init__(self, now=START):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, **kwargs):
        self.now += timedelta(**kwargs)


class FakeProvider:
    """Scripted Open-Meteo. `script` entries are consumed one per request; when it is
    empty the provider answers with `body`. An entry is a dict (JSON body), an int
    (error status), a str (non-JSON body), or an Exception (raised)."""

    def __init__(self):
        self.body = provider_body()
        self.script = []
        self.requests = []

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        item = self.script.pop(0) if self.script else self.body
        if isinstance(item, Exception):
            raise item
        if isinstance(item, int):
            return httpx.Response(item, json={"error": True, "reason": "boom"})
        if isinstance(item, str):
            return httpx.Response(200, content=item)
        return httpx.Response(200, content=json.dumps(item))

    @property
    def calls(self):
        return len(self.requests)

    def fail(self, times, how=None):
        """Next `times` requests fail with `how` (default: a 500)."""
        self.script = [how if how is not None else 500] * times


def make_settings(**overrides):
    values = dict(
        provider_base_url="http://provider",
        provider_api_key="",
        provider_timeout_seconds=1.0,
        provider_retries=2,
        provider_retry_pause_seconds=0.0,
        fresh_seconds=3 * 3600,
        max_stale_seconds=24 * 3600,
    )
    values.update(overrides)
    return Settings(_env_file=None, **values)


@pytest.fixture
def provider():
    return FakeProvider()


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def pauses():
    return []


@pytest.fixture
def client(provider, clock, pauses):
    app = create_app(
        settings=make_settings(),
        transport=httpx.MockTransport(provider.handle),
        clock=clock,
        sleep=pauses.append,
    )
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def forecast(client, lat=31.25, lon=34.79, days=7):
    return client.get("/v1/forecast", params={"lat": lat, "lon": lon, "days": days})


def assert_problem(response, status, code):
    assert response.status_code == status
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["code"] == code
    assert body["status"] == status
    return body
