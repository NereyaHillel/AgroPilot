from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from clients import Upstream
from config import Settings
from deps import get_upstream
from errors import register_error_handlers
from routers import plan

__all__ = ["app", "get_upstream"]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Read settings once, so a missing URL stops startup instead of failing every request.
    settings = Settings()
    app.state.upstream = Upstream(settings.registry_url, settings.weather_url, settings.upstream_timeout_seconds)
    yield
    app.state.upstream.close()


app = FastAPI(title="AgroPilot planner-service", version="0.1.0", lifespan=lifespan)
register_error_handlers(app)
app.include_router(plan.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
