# weather-service design

Date: 2026-11-12. Source: `tasks/p2.md` section "The weather-service" (FR-2.3 to FR-2.8, NFR-2.3) plus the decisions below.

## Intent

The planner has to answer "should I water this plot today, and for how long?". That answer depends on the weather. weather-service fetches the daily forecast from Open-Meteo, keeps it for a while, and serves it to the rest of the system. It knows coordinates and dates only; it knows nothing about farms, plots or crops.

## Goals

- `GET /v1/forecast?lat&lon&days` returns, for each of the next `days` days starting today, the date, ET0 (mm) and rain (mm).
- Points in the same 0.1 degree grid cell share one forecast. A forecast is fresh for 3 hours, and while it is fresh the provider is not called.
- When the provider fails, the service retries twice, then serves the last forecast it has for that cell with `stale: true`. With no earlier forecast it answers 503 `UNAVAILABLE` with `Retry-After`.
- Fresh answers meet p95 <= 100 ms at 10 requests per second (NFR-2.3).

## Non-goals

- No database. The cache lives in the memory of the process, and a restart empties it.
- No knowledge of farms, plots or crops.
- No other endpoints beyond `/v1/forecast` and `/health`.

## Anti-goals

- **Never answer with numbers the provider did not give** (FR-2.8). No zeros, no defaults, no filling a missing day. A forecast of zeros reads as "no water needed", which is the worst bug in this system. If a value is missing, that is a provider failure, not a zero.
- Open-Meteo's field names never leave the code that calls it.
- Never serve a forecast older than the stale limit, even marked `stale: true`.

## Constraints

- Python service under `services/weather-service/`, with its own `.venv` and `.env`. It never imports other services' code.
- Settings are read with pydantic-settings in one `config.py`. A missing required variable stops startup with a clear error. `.env` is never committed; `.env.example` is, with every variable.
- Variables in `.env`: provider base URL, request timeout, number of retries, freshness time, maximum stale age, API key (may be empty).
- Calls to Open-Meteo use `httpx`.
- The README names the Open-Meteo daily variables that give ET0 and rain, with their units (to be checked in the Open-Meteo docs), and explains the stale limit.

## Decisions

Decided by you:

- The cache is a per-process in-memory dictionary keyed by the 0.1 degree grid cell.
- A forecast is fresh for 3 hours.
- The maximum stale age is **24 hours**, set as `MAX_STALE_SECONDS`. Reasoning for the README: it covers a day-long provider outage, the forecast still covers today and most of the week, and rain predictions are still useful at that age. A longer limit risks "no irrigation" based on rain that never came; a shorter one gives growers no plan during short outages.
- Validation: lat -90 to 90, lon -180 to 180, days 1 to 7. Otherwise 422 `VALIDATION`.

My calls (confirm or change):

- **Stack:** FastAPI, `uv`, pydantic-settings, `httpx`, pytest. This matches registry-service, except that registry-service currently reads its settings with `python-dotenv`, not pydantic-settings.
- **Grid cell:** coordinates are rounded to the nearest 0.1 degree (see "More calls" for how), and Open-Meteo is called with the cell's coordinates. The response echoes the `lat` and `lon` the caller sent.
- **Always fetch 7 days** from the provider. The cache holds the whole week per cell, and `days` only slices the answer. A request for 3 days and one for 7 days therefore share a cache entry.
- **Retries:** "retries twice" means 1 attempt plus 2 retries, 3 in total. The number of retries is configurable.
- **What counts as a provider failure:** timeout, connection error, non-2xx status, a body that is not JSON, a missing field, a non-numeric value, a `null` value in any of the 7 days, or a daily array of the wrong length. Any one of these triggers the retry and stale path.
- **Missing days on a stale forecast:** a cached forecast keeps the dates it was fetched with. When serving a stale forecast, days before today (in the forecast's own date convention) are dropped, and the answer contains only the days the cache actually has. If today is no longer in the forecast, the answer is 503 `UNAVAILABLE`. Consumers must handle an answer with fewer days than requested; the planner design decides what it does then.
- **Dates:** the provider is asked for dates in the point's local timezone, so "today" is the point's local today.
- **Fields:** `fetched_at` is the UTC time the provider was last successfully called, and a stale answer keeps the old `fetched_at`. `source` is `"open-meteo"`.
- **Errors** use RFC 9457 `application/problem+json` with a `code` field, as registry-service does. `Retry-After` on 503 is a small constant.
- **`/health`** returns `{"status": "ok"}`, like registry-service, so the frontend status line can call it.
- **Tests** run against a fake provider, never the real network. They cover validation, the grid cell sharing, freshness, retry, stale, the stale limit, 503 and every kind of malformed provider body.

## Response contract

From the spec's example, so the planner can rely on it. The body is `{lat, lon, source, fetched_at, stale, days}`. `stale` is always present (true or false). Each element of `days` is `{date, et0_mm, rain_mm}`. A fresh answer always has exactly the requested number of days. Only a stale answer can have fewer, and it carries no extra field saying so; the consumer compares the length of `days` with what it asked for.

## More calls, added after review (confirm or change)

- **Local date:** the service asks Open-Meteo for `timezone=auto` and stores the returned UTC offset with the cache entry. "Today" for a cache entry is computed from the current UTC time plus that offset.
- **Freshness across midnight:** an entry is fresh only while it is under 3 hours old and its first date is still today. After local midnight it counts as not fresh, so the service tries the provider again. If the provider fails, the normal stale rule applies and yesterday's day is dropped. This stops yesterday's numbers being served as today's.
- **Variables:** ET0 is the daily `et0_fao_evapotranspiration` and rain is the daily `rain_sum`, both in mm. `precipitation_sum` is not used because it includes snow. The builder confirms both names and units in the Open-Meteo docs and records them in the README.
- **API key:** when non-empty, it is sent as the `apikey` query parameter, which is how Open-Meteo's paid tier works. The base URL is a variable, so moving to the paid host or another provider is a config change.
- **Retries:** the timeout applies to each attempt. There is a short fixed pause between attempts, set in `.env`. A 4xx or 5xx status is a failure and is retried like any other, as FR-2.6 says.
- **Grid cell key:** built from integer tenths of a degree with half-up rounding, with `-0.0` treated as `0.0`. This replaces `round(x, 1)` from the earlier calls, which rounds inconsistently on binary floats.
- **Cache size:** no size cap. Entries older than the stale limit can never be served, so they are removed.
- **503 body:** `Retry-After` is a header, and the body is the usual problem document with a `detail`.

## Left to the builder

- Module layout, the HTTP client's lifecycle and how the fake provider is wired into tests.
- Whether concurrent requests for the same cold cell share one provider call.
- The exact clock abstraction used to test freshness and the stale limit.
- Whether to add the optional Mermaid sequence diagram to the README.
