import pytest

from conftest import assert_problem, forecast, provider_body


def test_returns_the_documented_shape(client, provider):
    provider.body = provider_body(et0=[3.1, 2.8, 2.5, 2.9, 3.0, 3.3, 3.2], rain=[0, 4.2, 0, 0, 1.0, 0, 0])
    response = forecast(client)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"lat", "lon", "source", "fetched_at", "stale", "days"}
    assert body["lat"] == 31.25 and body["lon"] == 34.79
    assert body["source"] == "open-meteo"
    assert body["fetched_at"] == "2026-11-12T06:00:00Z"
    assert body["stale"] is False
    assert len(body["days"]) == 7
    assert body["days"][0] == {"date": "2026-11-12", "et0_mm": 3.1, "rain_mm": 0.0}
    assert body["days"][1] == {"date": "2026-11-13", "et0_mm": 2.8, "rain_mm": 4.2}


def test_days_slices_the_cached_week(client, provider):
    assert len(forecast(client, days=3).json()["days"]) == 3
    assert len(forecast(client, days=7).json()["days"]) == 7
    assert provider.calls == 1  # always fetches 7 days, so both share one entry


def test_provider_is_asked_for_the_cell_centre_in_local_time(client, provider):
    forecast(client, lat=31.25, lon=34.79)
    params = dict(provider.requests[0].url.params)
    assert params["latitude"] == "31.3"
    assert params["longitude"] == "34.8"
    assert params["timezone"] == "auto"
    assert params["forecast_days"] == "7"
    assert params["daily"] == "et0_fao_evapotranspiration,rain_sum"
    assert "apikey" not in params


@pytest.mark.parametrize(
    "params",
    [
        {"lat": 90.1, "lon": 0, "days": 1},
        {"lat": -90.1, "lon": 0, "days": 1},
        {"lat": 0, "lon": 180.1, "days": 1},
        {"lat": 0, "lon": -180.1, "days": 1},
        {"lat": 0, "lon": 0, "days": 0},
        {"lat": 0, "lon": 0, "days": 8},
        {"lat": "x", "lon": 0, "days": 1},
        {"lat": 0, "lon": 0, "days": "x"},
        {"lat": 0, "lon": 0, "days": 2.5},
        {"lat": "nan", "lon": 0, "days": 1},
        {"lat": "inf", "lon": 0, "days": 1},
        {"lon": 0, "days": 1},
        {"lat": 0, "days": 1},
        {"lat": 0, "lon": 0},
    ],
)
def test_bad_parameters_are_422_validation(client, provider, params):
    assert_problem(client.get("/v1/forecast", params=params), 422, "VALIDATION")
    assert provider.calls == 0


@pytest.mark.parametrize("lat,lon,days", [(90, 180, 7), (-90, -180, 1), (0, 0, 1)])
def test_boundaries_are_accepted(client, lat, lon, days):
    assert forecast(client, lat=lat, lon=lon, days=days).status_code == 200


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_unknown_route_and_method_are_problem_json(client):
    assert_problem(client.get("/v1/nothing"), 404, "NOT_FOUND")
    assert_problem(client.post("/v1/forecast"), 405, "VALIDATION")
