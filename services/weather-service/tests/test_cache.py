from datetime import UTC, date, datetime

import pytest

from cache import cell_key
from conftest import forecast, provider_body


@pytest.mark.parametrize(
    "lat,lon,expected",
    [
        (31.25, 34.79, (313, 348)),   # 31.25 rounds half up to 31.3
        (31.24, 34.74, (312, 347)),
        (31.249999, 34.7500001, (312, 348)),
        (0.05, 0.05, (1, 1)),          # float 0.05 is below 0.05 in binary; decimal half-up gives 0.1
        (-0.04, -0.04, (0, 0)),
        (-0.0, -0.0, (0, 0)),          # no "-0.0" cell
        (-0.05, -0.05, (-1, -1)),      # half rounds away from zero, symmetric around 0
        (90, 180, (900, 1800)),
        (-90, -180, (-900, -1800)),
    ],
)
def test_cell_key_uses_decimal_half_up_tenths(lat, lon, expected):
    assert cell_key(lat, lon) == expected


def test_points_in_the_same_cell_share_a_forecast(client, provider):
    first = forecast(client, lat=31.25, lon=34.79).json()
    second = forecast(client, lat=31.34, lon=34.75).json()
    assert provider.calls == 1
    assert second["days"] == first["days"]
    # The answer echoes the caller's own coordinates, not the cell's.
    assert (second["lat"], second["lon"]) == (31.34, 34.75)


def test_points_in_different_cells_do_not_share(client, provider):
    forecast(client, lat=31.25, lon=34.79)
    forecast(client, lat=31.45, lon=34.79)
    assert provider.calls == 2


def test_fresh_forecast_does_not_call_the_provider_again(client, provider, clock):
    forecast(client)
    clock.advance(hours=2, minutes=59)
    body = forecast(client).json()
    assert provider.calls == 1
    assert body["stale"] is False
    assert body["fetched_at"] == "2026-11-12T06:00:00Z"


def test_forecast_older_than_3_hours_is_fetched_again(client, provider, clock):
    forecast(client)
    clock.advance(hours=3)
    provider.body = provider_body(et0=[9.9] * 7)
    body = forecast(client).json()
    assert provider.calls == 2
    assert body["days"][0]["et0_mm"] == 9.9
    assert body["fetched_at"] == "2026-11-12T09:00:00Z"


def test_forecast_is_not_fresh_after_local_midnight(client, provider, clock):
    # Zone UTC+2. Fetched at 21:00 UTC (23:00 local on the 12th); at 22:30 UTC it is
    # 00:30 local on the 13th, only 1.5 h later, yet the entry's first day is yesterday.
    clock.now = datetime(2026, 11, 12, 21, 0, tzinfo=UTC)
    provider.body = provider_body(first=date(2026, 11, 12), offset=7200)
    forecast(client)
    clock.now = datetime(2026, 11, 12, 21, 59, tzinfo=UTC)
    forecast(client)
    assert provider.calls == 1  # same local day: still fresh
    clock.now = datetime(2026, 11, 12, 22, 30, tzinfo=UTC)
    provider.body = provider_body(first=date(2026, 11, 13), offset=7200)
    body = forecast(client).json()
    assert provider.calls == 2
    assert body["days"][0]["date"] == "2026-11-13"
    assert body["stale"] is False
