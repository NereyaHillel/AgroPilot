from datetime import date
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

# Upstream numbers must be real numbers: a string, null or NaN is an upstream failure, never a zero.
Number = Annotated[float, Field(strict=True, allow_inf_nan=False)]
PositiveNumber = Annotated[float, Field(strict=True, gt=0, allow_inf_nan=False)]


class SoilState(StrEnum):
    """How wet the soil was the day before the plan."""

    dry = "dry"
    half = "half"
    wet = "wet"


class RegistryPlot(BaseModel):
    area_m2: PositiveNumber
    crop_id: str
    planting_date: date
    soil_id: str
    row_spacing_m: PositiveNumber
    emitter_spacing_m: PositiveNumber
    emitter_id: str
    lat: Number
    lon: Number


class RegistrySoil(BaseModel):
    available_water_mm_per_m: PositiveNumber


class RegistryEmitter(BaseModel):
    flow_lph: PositiveNumber


class ForecastDay(BaseModel):
    date: date
    et0_mm: Number
    rain_mm: Number


class Forecast(BaseModel):
    stale: bool = Field(strict=True)
    days: list[ForecastDay] = Field(min_length=1)


class PlanDay(BaseModel):
    date: date
    et0_mm: float
    kc: float
    need_mm: float
    litres: float
    run_minutes: float
    stale: bool
    bucket_end_mm: float


class Plan(BaseModel):
    plot_id: str
    bucket_capacity_mm: float
    trigger_mm: float
    days: list[PlanDay]
