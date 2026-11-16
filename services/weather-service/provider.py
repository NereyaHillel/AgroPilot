"""Open-Meteo client. Its field names never leave this module.

Daily variables (units mm): et0_fao_evapotranspiration -> ET0, rain_sum -> rain.
Any answer that is not complete and numeric is a ProviderError; nothing is ever filled in.
"""

import json
import math
from dataclasses import dataclass
from datetime import date, timedelta

import httpx

FORECAST_DAYS = 7
_ET0 = "et0_fao_evapotranspiration"
_RAIN = "rain_sum"
_MAX_OFFSET_SECONDS = 24 * 3600 # maximum allowed UTC offset in seconds (24 hours)  


class ProviderError(Exception):
    """The provider did not give a usable forecast."""


@dataclass(frozen=True)
class Day:
    date: date
    et0_mm: float
    rain_mm: float


@dataclass(frozen=True)
class ProviderForecast:
    days: tuple[Day, ...]
    utc_offset_seconds: int


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and math.isfinite(value)


def parse(content: bytes) -> ProviderForecast:
    try:
        body = json.loads(content)
        offset = body["utc_offset_seconds"]
        daily = body["daily"]
        times, et0, rain = daily["time"], daily[_ET0], daily[_RAIN]
    except (ValueError, KeyError, TypeError):
        raise ProviderError("body is not JSON or a field is missing") from None
    if isinstance(offset, bool) or not isinstance(offset, int) or abs(offset) > _MAX_OFFSET_SECONDS:
        raise ProviderError("bad utc_offset_seconds")
    for series in (times, et0, rain):
        if not isinstance(series, list) or len(series) != FORECAST_DAYS:
            raise ProviderError(f"daily arrays must have {FORECAST_DAYS} entries")
    if not all(_is_number(v) for v in et0 + rain):
        raise ProviderError("a daily value is null or not a number")
    try:
        dates = [date.fromisoformat(t) for t in times]
    except (TypeError, ValueError):
        raise ProviderError("bad date") from None
    if any(b - a != timedelta(days=1) for a, b in zip(dates, dates[1:])):
        raise ProviderError("dates are not consecutive")
    days = tuple(Day(d, float(e), float(r)) for d, e, r in zip(dates, et0, rain))
    return ProviderForecast(days, offset)


class OpenMeteo:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout_seconds: float,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._http = httpx.Client(timeout=timeout_seconds, transport=transport)

    def close(self) -> None:
        self._http.close()

    def fetch(self, lat: float, lon: float) -> ProviderForecast:
        """One attempt: the next 7 days from today, in the point's local time."""
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": f"{_ET0},{_RAIN}",
            "timezone": "auto",
            "forecast_days": FORECAST_DAYS,
        }
        if self._api_key:
            params["apikey"] = self._api_key
        try:
            response = self._http.get(f"{self._base_url}/v1/forecast", params=params)
        except httpx.HTTPError as error:
            raise ProviderError(f"request failed: {type(error).__name__}") from None
        if not response.is_success:
            raise ProviderError(f"status {response.status_code}")
        return parse(response.content)
