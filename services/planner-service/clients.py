"""HTTP clients for registry-service and weather-service.

Every failure to get a usable answer becomes UpstreamUnavailable naming the
service, so the planner can never turn a missing forecast into a plan of zeros.
"""

import httpx
from pydantic import BaseModel, ValidationError

from errors import NotFoundProblem, UpstreamUnavailable
from schemas import Forecast, RegistryEmitter, RegistryPlot, RegistrySoil

REGISTRY = "registry-service"
WEATHER = "weather-service"


class Upstream:
    def __init__(
        self,
        registry_url: str,
        weather_url: str,
        timeout_seconds: float,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._registry_url = registry_url
        self._weather_url = weather_url
        self._http = httpx.Client(timeout=timeout_seconds, transport=transport)

    def close(self) -> None:
        self._http.close()

    def get_plot(self, plot_id: str) -> RegistryPlot:
        response = self._get(REGISTRY, f"{self._registry_url}/v1/plots/{plot_id}")
        if response.status_code == 404:
            raise NotFoundProblem(f"Plot {plot_id} not found")
        return self._parse(REGISTRY, response, RegistryPlot)

    def get_soil(self, soil_id: str) -> RegistrySoil:
        response = self._get(REGISTRY, f"{self._registry_url}/v1/soils/{soil_id}")
        return self._parse(REGISTRY, response, RegistrySoil)

    def get_emitter(self, emitter_id: str) -> RegistryEmitter:
        response = self._get(REGISTRY, f"{self._registry_url}/v1/emitters/{emitter_id}")
        return self._parse(REGISTRY, response, RegistryEmitter)

    def get_forecast(self, lat: float, lon: float, days: int) -> Forecast:
        response = self._get(
            WEATHER, f"{self._weather_url}/v1/forecast", {"lat": lat, "lon": lon, "days": days}
        )
        return self._parse(WEATHER, response, Forecast)

    def _get(self, service: str, url: str, params: dict | None = None) -> httpx.Response:
        try:
            return self._http.get(url, params=params)
        except httpx.TimeoutException:
            raise UpstreamUnavailable(service, "did not answer in time") from None
        except httpx.HTTPError:
            raise UpstreamUnavailable(service, "is unreachable") from None

    @staticmethod
    def _parse[T: BaseModel](service: str, response: httpx.Response, model: type[T]) -> T:
        if response.status_code != 200:
            raise UpstreamUnavailable(service, f"answered with status {response.status_code}")
        try:
            return model.model_validate_json(response.content)
        except ValidationError:
            raise UpstreamUnavailable(service, "returned an unusable response") from None
