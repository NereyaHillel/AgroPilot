from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from clients import Upstream
from deps import get_upstream
from plan import build_plan
from schemas import Plan

router = APIRouter(prefix="/v1/plots", tags=["plan"])


@router.get("/{plot_id}/plan", response_model=Plan)
def get_plan(
    plot_id: UUID,
    upstream: Annotated[Upstream, Depends(get_upstream)],
    days: Annotated[int, Query(ge=1, le=7)] = 7,
) -> dict[str, Any]:
    plot = upstream.get_plot(str(plot_id))
    soil = upstream.get_soil(plot.soil_id)
    emitter = upstream.get_emitter(plot.emitter_id)
    forecast = upstream.get_forecast(plot.lat, plot.lon, days)
    return {"plot_id": str(plot_id), **build_plan(plot, soil, emitter, forecast, days)}
