"""Fake registry-service and weather-service behind httpx.MockTransport."""

import json
from datetime import date, timedelta

import httpx
import pytest
from fastapi.testclient import TestClient

from clients import Upstream
from main import app, get_upstream

PLOT_ID = "c8f3d1b0-4d2e-5a1b-8b22-1d6e3f702002"
FIRST_DAY = date(2026, 6, 1)


def forecast_days(count=7, et0=5.0, rain=0.0, start=FIRST_DAY):
    return [
        {"date": (start + timedelta(days=i)).isoformat(), "et0_mm": et0, "rain_mm": rain}
        for i in range(count)
    ]


class World:
    """What the two fake services answer. Tests change the attributes."""

    def __init__(self):
        # Tomato, sand, 0.6 L/h on 1.5 x 0.4 m (1.0 mm/h), 1500 m2.
        # Planted 99 days before FIRST_DAY, so day 1 of the plan is season day 100 (Kc mid).
        self.plot = {
            "id": PLOT_ID, "farm_id": "b7e2c0a0-3c1d-4f0a-9a11-0c5d2e6f1001", "name": "West block",
            "area_m2": 1500.0, "crop_id": "tomato",
            "planting_date": (FIRST_DAY - timedelta(days=99)).isoformat(),
            "soil_id": "sand", "row_spacing_m": 1.5, "emitter_spacing_m": 0.4,
            "emitter_id": "dripnet-pc-0.6", "lat": 31.4, "lon": 34.6,
        }
        self.soil = {"id": "sand", "name": "Sand", "available_water_mm_per_m": 83}
        self.emitter = {"id": "dripnet-pc-0.6", "name": "DripNet PC", "flow_lph": 0.6}
        self.forecast = {
            "lat": 31.4, "lon": 34.6, "source": "open-meteo",
            "fetched_at": "2026-06-01T05:00:00Z", "stale": False, "days": forecast_days(),
        }
        # None = answer normally; an Exception is raised; an int is an error status;
        # a str is sent as a non-JSON body.
        self.registry_fault = None
        self.weather_fault = None
        self.weather_requests = []

    def _fault(self, fault):
        if isinstance(fault, Exception):
            raise fault
        if isinstance(fault, int):
            return httpx.Response(fault, json={"detail": "boom"})
        if isinstance(fault, str):
            return httpx.Response(200, content=fault)
        return None

    def handle(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.url.host == "weather":
            self.weather_requests.append(dict(request.url.params))
            return self._fault(self.weather_fault) or httpx.Response(200, json=self.forecast)
        fault = self._fault(self.registry_fault)
        if fault:
            return fault
        if path == f"/v1/plots/{PLOT_ID}":
            return httpx.Response(200, json=self.plot)
        if path == f"/v1/soils/{self.plot['soil_id']}":
            return httpx.Response(200, json=self.soil)
        if path == f"/v1/emitters/{self.plot['emitter_id']}":
            return httpx.Response(200, json=self.emitter)
        return httpx.Response(
            404, json={"code": "NOT_FOUND", "detail": "not found"},
            headers={"content-type": "application/problem+json"},
        )


@pytest.fixture
def world():
    return World()


@pytest.fixture
def client(world, monkeypatch):
    monkeypatch.setenv("REGISTRY_URL", "http://registry")
    monkeypatch.setenv("WEATHER_URL", "http://weather")
    upstream = Upstream("http://registry", "http://weather", 1.0, transport=httpx.MockTransport(world.handle))
    app.dependency_overrides[get_upstream] = lambda: upstream
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def assert_problem(response, status, code):
    assert response.status_code == status
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["code"] == code
    assert body["status"] == status
    return body


__all__ = ["PLOT_ID", "FIRST_DAY", "World", "forecast_days", "assert_problem", "json"]
