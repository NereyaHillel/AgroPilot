from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated

import httpx
from fastapi import FastAPI, Query, Request

from config import Settings
from errors import register_error_handlers
from provider import OpenMeteo
from schemas import ForecastResponse
from service import ForecastService

SOURCE = "open-meteo"


def create_app(
    settings: Settings | None = None,
    transport: httpx.BaseTransport | None = None,
    clock: Callable[[], datetime] | None = None,
    sleep: Callable[[float], None] | None = None,
) -> FastAPI:
    """Arguments other than settings exist so tests can fake the network and the clock."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Settings() raises with the names of any missing variable, so a bad .env stops startup.
        config = settings or Settings()
        provider = OpenMeteo(
            config.provider_base_url, config.provider_api_key, config.provider_timeout_seconds, transport
        )
        extra = {k: v for k, v in {"clock": clock, "sleep": sleep}.items() if v is not None}
        app.state.service = ForecastService(provider, config, **extra)
        yield
        provider.close()

    app = FastAPI(title="AgroPilot weather-service", version="0.1.0", lifespan=lifespan)
    register_error_handlers(app)

    @app.get("/v1/forecast", response_model=ForecastResponse)
    def get_forecast(
        request: Request,
        lat: Annotated[float, Query(ge=-90, le=90, allow_inf_nan=False)],
        lon: Annotated[float, Query(ge=-180, le=180, allow_inf_nan=False)],
        days: Annotated[int, Query(ge=1, le=7)],
    ) -> dict:
        result = request.app.state.service.get(lat, lon, days)
        return {
            "lat": lat,
            "lon": lon,
            "source": SOURCE,
            "fetched_at": result.fetched_at.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stale": result.stale,
            "days": [
                {"date": d.date, "et0_mm": d.et0_mm, "rain_mm": d.rain_mm} for d in result.days
            ],
        }

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
