# weather-service: overview

Port **8001**. Fetches the daily forecast from Open-Meteo, keeps it in memory and serves reference evapotranspiration (ET0) and rain to the rest of the system. It knows only coordinates and dates: nothing about farms, plots, soils or crops.

## Responsibilities

- Serve `GET /v1/forecast?lat&lon&days` with `et0_mm` and `rain_mm` for 1 to 7 days starting today.
- Cache forecasts per 0.1° grid cell so repeated requests do not hit the provider.
- Survive provider failures: retry, then serve a recent stale forecast, then fail honestly.
- **Never invent data.** A missing, `null` or non-numeric value is a provider failure. A fake `0.0` would tell a grower "no irrigation needed", which is the worst possible silent bug.

## Tech stack

Python, FastAPI, Pydantic v2, `pydantic-settings`, `httpx`, `uv`, pytest.

## Code layout

| File | Role |
|---|---|
| `main.py` | `create_app()` with injectable settings, transport, clock and sleep (so tests fake the network and time). Routes and `/health` |
| `config.py` | `Settings` (pydantic-settings). Every variable except the API key is required; a bad `.env` stops startup. Checks that the stale limit is not shorter than the freshness window |
| `provider.py` | The only module that knows Open-Meteo. Builds the request, validates the whole answer, returns plain `Day` objects |
| `cache.py` | Grid cell key (`cell_key`) and the cached `Entry` |
| `service.py` | `ForecastService`: the fresh / retry / stale / 503 decision, locking |
| `schemas.py` | Response models |
| `errors.py` | `application/problem+json` errors, `503 UNAVAILABLE` with `Retry-After` |

## API

`GET /v1/forecast?lat={lat}&lon={lon}&days={days}`

```json
{
  "lat": 31.25, "lon": 34.79, "source": "open-meteo",
  "fetched_at": "2026-11-12T06:00:00Z", "stale": false,
  "days": [
    {"date": "2026-11-12", "et0_mm": 3.1, "rain_mm": 0.0},
    {"date": "2026-11-13", "et0_mm": 2.8, "rain_mm": 4.2}
  ]
}
```

| Status | `code` | When |
|---|---|---|
| 422 | `VALIDATION` | `lat` outside -90..90, `lon` outside -180..180, `days` outside 1..7, or missing or malformed |
| 503 | `UNAVAILABLE` | provider failed and no usable cached forecast exists. Includes `Retry-After` |
| 500 | `INTERNAL` | a bug |

`GET /health` returns `{"status": "ok"}`.

## How a request is decided

1. Round `lat` and `lon` to the 0.1° cell (decimal arithmetic, half rounds away from zero). Points in the same cell share one entry.
2. **Fresh hit:** the entry is younger than `FRESH_SECONDS` (3 h) **and** its first day is still today in the point's local time. Serve it, with no provider call.
3. **Miss or not fresh:** call the provider for the cell centre, 7 days, in local time (`timezone=auto`). One attempt plus `PROVIDER_RETRIES` retries, with a pause between attempts.
4. **Success:** store the entry, return `stale: false`.
5. **All attempts failed:** if an entry exists, is not older than `MAX_STALE_SECONDS` (24 h) and still contains today, return it with `stale: true` (days already in the past are dropped, so the list can be shorter than requested). Otherwise return `503 UNAVAILABLE`.

Details that matter:
- The cache always stores 7 days, so a request for 3 days and one for 7 share an entry.
- A forecast is never served as "today" after local midnight if its first day is yesterday.
- Concurrent requests for one cold cell trigger a single provider call (per-cell lock). A global mutex guards the dictionaries but is never held during a network call.
- Entries older than the stale limit are removed when a new forecast is stored. The cache is per process, so a restart empties it. There is no external store.

## Open-Meteo anti-corruption layer

The provider's field names exist only in `provider.py`.

| Output field | Open-Meteo daily variable | Unit |
|---|---|---|
| `et0_mm` | `et0_fao_evapotranspiration` (FAO-56 Penman-Monteith reference ET) | mm |
| `rain_mm` | `rain_sum` (liquid rain only) | mm |

`precipitation_sum` is deliberately not used because it includes snow. The parser rejects the response unless it has exactly 7 entries per series, all numeric and finite, consecutive dates and a sane `utc_offset_seconds`.

## Configuration

| Variable | Meaning |
|---|---|
| `PROVIDER_BASE_URL` | `https://api.open-meteo.com` |
| `PROVIDER_API_KEY` | Optional; sent as `apikey` when set |
| `PROVIDER_TIMEOUT_SECONDS` | Timeout per attempt |
| `PROVIDER_RETRIES` | Retries after the first failure (2 means 3 attempts) |
| `PROVIDER_RETRY_PAUSE_SECONDS` | Pause between attempts |
| `FRESH_SECONDS` | Freshness window, 10800 (3 h) |
| `MAX_STALE_SECONDS` | Oldest forecast served as stale, 86400 (24 h) |

The spec names `OPEN_METEO_BASE_URL`, `HTTP_TIMEOUT_SECONDS`, `MAX_RETRIES`, `CACHE_FRESHNESS_SECONDS`, `CACHE_MAX_STALE_SECONDS` and `WEATHER_API_KEY`. The code uses shorter provider-neutral names, so check them against the spec before review.

## Why 24 hours of staleness

A day-long outage still gives growers a plan, and the forecast still covers today and most of the week. Rain predictions stay useful at that age. Going longer risks a forecast of rain that never came, which leads to "no irrigation". Going shorter leaves growers with nothing during short outages.

## Tests and performance

- 102 tests, no network: the provider and the clock are faked. They cover cache keys, config validation, forecast flow and every provider failure mode.
- NFR-2.3 (fresh requests p95 ≤ 100 ms at 10 req/s): **8.4 ms p95**, median 6.2 ms, 600 requests, 0 failures. This is a 60 s run against one cached cell, not a longer soak.

## Known limits

- A stale answer can have fewer days than requested, with no flag saying so. The caller compares lengths.
- The cache is in memory and per process. Running several workers would give each its own cache.
