"""FR-2.6 to FR-2.8: retries, stale answers, the stale limit and 503."""

from datetime import UTC, date, datetime

import httpx
import pytest

from conftest import assert_problem, forecast, provider_body

BAD_BODIES = {
    "timeout": httpx.ReadTimeout("slow"),
    "connection error": httpx.ConnectError("refused"),
    "error status": 500,
    "client error status": 429,
    "not json": "<html>oops</html>",
    "json but not an object": "[1, 2, 3]",
    "no daily": {"utc_offset_seconds": 0},
    "no et0": {"utc_offset_seconds": 0, "daily": {"time": ["2026-11-12"] * 7, "rain_sum": [0] * 7}},
    "no rain": {"utc_offset_seconds": 0, "daily": {"time": ["2026-11-12"] * 7, "et0_fao_evapotranspiration": [1] * 7}},
    "no offset": {"daily": provider_body()["daily"]},
    "null et0 value": provider_body(et0=[3.1, None, 2.5, 2.9, 3.0, 3.3, 3.2]),
    "null rain value": provider_body(rain=[0, None, 0, 0, 0, 0, 0]),
    "text et0 value": provider_body(et0=[3.1, "wet", 2.5, 2.9, 3.0, 3.3, 3.2]),
    "bool value": provider_body(et0=[True] * 7),
    "nan value": '{"utc_offset_seconds": 0, "daily": {"time": ["2026-11-12","2026-11-13","2026-11-14","2026-11-15","2026-11-16","2026-11-17","2026-11-18"], "et0_fao_evapotranspiration": [NaN,1,1,1,1,1,1], "rain_sum": [0,0,0,0,0,0,0]}}',
    "too few days": provider_body(count=6),
    "too many days": provider_body(count=8),
    "gap in dates": {**provider_body(), "daily": {**provider_body()["daily"], "time": ["2026-11-12", "2026-11-14"] + ["2026-11-15"] * 5}},
    "bad date": {**provider_body(), "daily": {**provider_body()["daily"], "time": ["soon"] * 7}},
    "text offset": {**provider_body(), "utc_offset_seconds": "later"},
}


@pytest.fixture(params=BAD_BODIES.values(), ids=BAD_BODIES.keys())
def bad(request):
    return request.param


def test_cold_cell_with_a_bad_provider_is_503_unavailable(client, provider, bad):
    provider.script = [bad] * 3
    response = forecast(client)
    body = assert_problem(response, 503, "UNAVAILABLE")
    assert response.headers["retry-after"]
    assert "days" not in body  # never a plan of zeros
    assert provider.calls == 3


def test_retries_twice_then_gives_up_and_pauses_between_attempts(client, provider, pauses):
    provider.fail(10)
    assert forecast(client).status_code == 503
    assert provider.calls == 3  # 1 attempt + 2 retries
    assert len(pauses) == 2  # none after the last attempt


def test_second_attempt_can_succeed(client, provider):
    provider.script = [500]
    response = forecast(client)
    assert response.status_code == 200
    assert response.json()["stale"] is False
    assert provider.calls == 2


def test_provider_failure_serves_the_last_forecast_as_stale(client, provider, clock):
    forecast(client)
    clock.advance(hours=4)
    provider.fail(3)
    response = forecast(client)
    assert response.status_code == 200
    body = response.json()
    assert body["stale"] is True
    assert body["fetched_at"] == "2026-11-12T06:00:00Z"  # keeps the old time
    assert len(body["days"]) == 7
    assert body["days"][0]["date"] == "2026-11-12"
    assert provider.calls == 4


def test_stale_answer_works_for_every_kind_of_bad_provider(client, provider, clock, bad):
    forecast(client)
    clock.advance(hours=4)
    provider.script = [bad] * 3
    assert forecast(client).json()["stale"] is True


def test_provider_recovers_after_a_stale_answer(client, provider, clock):
    forecast(client)
    clock.advance(hours=4)
    provider.fail(3)
    assert forecast(client).json()["stale"] is True
    provider.body = provider_body(et0=[8.0] * 7)
    body = forecast(client).json()
    assert body["stale"] is False
    assert body["days"][0]["et0_mm"] == 8.0


def test_a_failed_refresh_does_not_overwrite_the_good_forecast(client, provider, clock):
    first = forecast(client).json()
    clock.advance(hours=4)
    provider.fail(3, how=provider_body(et0=[None] * 7))
    assert forecast(client).json()["days"] == first["days"]


def test_forecast_at_exactly_the_stale_limit_is_still_served(client, provider, clock):
    forecast(client)
    clock.advance(hours=24)
    provider.fail(3)
    assert forecast(client).json()["stale"] is True


def test_forecast_older_than_the_stale_limit_is_never_served(client, provider, clock):
    forecast(client)
    clock.advance(hours=24, seconds=1)
    provider.fail(3)
    assert_problem(forecast(client), 503, "UNAVAILABLE")


def test_stale_forecast_drops_days_before_today(client, provider, clock):
    forecast(client)  # days 12..18, fetched 06:00 on the 12th
    clock.now = datetime(2026, 11, 13, 5, 0, tzinfo=UTC)  # 23 h later: today is the 13th
    provider.fail(3)
    body = forecast(client).json()
    assert body["stale"] is True
    assert [d["date"] for d in body["days"]] == [
        "2026-11-13", "2026-11-14", "2026-11-15", "2026-11-16", "2026-11-17", "2026-11-18",
    ]


def test_stale_answer_may_have_fewer_days_than_asked(client, provider, clock):
    forecast(client)
    clock.now = datetime(2026, 11, 13, 5, 0, tzinfo=UTC)
    provider.fail(3)
    assert len(forecast(client, days=7).json()["days"]) == 6
    assert len(forecast(client, days=2).json()["days"]) == 2


def test_stale_without_today_is_503_even_inside_the_stale_limit(client, provider, clock):
    # Local date is 22 h ahead of the entry's last day, entry only 23 h old, but today is not in it.
    provider.body = provider_body(first=date(2026, 11, 6), offset=0)  # days 6..12
    clock.now = datetime(2026, 11, 12, 6, 0, tzinfo=UTC)
    forecast(client)
    clock.now = datetime(2026, 11, 13, 5, 0, tzinfo=UTC)  # 23 h later, the 13th
    provider.fail(3)
    assert_problem(forecast(client), 503, "UNAVAILABLE")


def test_expired_entries_are_removed(client, provider, clock):
    forecast(client, lat=10.0, lon=10.0)
    clock.advance(hours=25)
    assert client.app.state.service.size == 1
    forecast(client, lat=20.0, lon=20.0)  # a new fetch sweeps the expired cell
    assert client.app.state.service.size == 1
    provider.fail(3)
    assert_problem(forecast(client, lat=10.0, lon=10.0), 503, "UNAVAILABLE")


def test_api_key_is_sent_only_when_set(provider, clock):
    import httpx as _httpx
    from fastapi.testclient import TestClient

    from conftest import make_settings
    from main import create_app

    app = create_app(
        settings=make_settings(provider_api_key="secret"),
        transport=_httpx.MockTransport(provider.handle), clock=clock, sleep=lambda s: None,
    )
    with TestClient(app) as c:
        forecast(c)
    assert provider.requests[0].url.params["apikey"] == "secret"
