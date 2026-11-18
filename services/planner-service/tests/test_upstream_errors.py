import httpx
import pytest

from conftest import assert_problem
from test_plan_api import get_plan

FAULTS = {
    "connection refused": httpx.ConnectError("refused"),
    "timeout": httpx.ReadTimeout("slow"),
    "server error": 500,
    "unavailable": 503,
    "not json": "<html>oops</html>",
}


@pytest.mark.parametrize("fault", FAULTS.values(), ids=FAULTS.keys())
def test_registry_failure_is_503_naming_registry(client, world, fault):
    world.registry_fault = fault
    body = assert_problem(get_plan(client), 503, "UPSTREAM_UNAVAILABLE")
    assert "registry-service" in body["detail"]
    assert "days" not in body


@pytest.mark.parametrize("fault", FAULTS.values(), ids=FAULTS.keys())
def test_weather_failure_is_503_naming_weather(client, world, fault):
    world.weather_fault = fault
    response = get_plan(client)
    body = assert_problem(response, 503, "UPSTREAM_UNAVAILABLE")
    assert "weather-service" in body["detail"]
    assert "days" not in body
    assert response.headers["retry-after"]


def test_registry_failure_wins_over_weather_when_both_are_down(client, world):
    world.registry_fault = 503
    world.weather_fault = 503
    assert "registry-service" in get_plan(client).json()["detail"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda f: f["days"][0].pop("et0_mm"),
        lambda f: f["days"][0].update(et0_mm=None),
        lambda f: f["days"][0].update(rain_mm=None),
        lambda f: f["days"][0].update(et0_mm="wet"),
        lambda f: f.update(days=[]),
        lambda f: f.pop("days"),
        lambda f: f.update(stale="maybe"),
    ],
    ids=["no-et0", "null-et0", "null-rain", "text-et0", "empty-days", "no-days", "bad-stale"],
)
def test_malformed_forecast_is_503_never_zeros(client, world, mutate):
    mutate(world.forecast)
    body = assert_problem(get_plan(client), 503, "UPSTREAM_UNAVAILABLE")
    assert "weather-service" in body["detail"]


def test_malformed_plot_from_registry_is_503(client, world):
    del world.plot["area_m2"]
    body = assert_problem(get_plan(client), 503, "UPSTREAM_UNAVAILABLE")
    assert "registry-service" in body["detail"]


def test_unexpected_error_is_problem_json_500(client, world, monkeypatch):
    import routers.plan

    monkeypatch.setattr(routers.plan, "build_plan", lambda *a, **k: 1 / 0)
    assert_problem(get_plan(client), 500, "INTERNAL")


def test_unknown_route_is_problem_json_404(client):
    assert_problem(client.get("/v1/nothing"), 404, "NOT_FOUND")


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
