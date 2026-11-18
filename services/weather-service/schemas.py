from datetime import date

from pydantic import BaseModel


class ForecastDay(BaseModel):
    date: date
    et0_mm: float
    rain_mm: float


class ForecastResponse(BaseModel):
    lat: float
    lon: float
    source: str
    fetched_at: str
    stale: bool
    days: list[ForecastDay]
