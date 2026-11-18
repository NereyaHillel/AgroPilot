# planner-service: overview

Port **8002**. Answers "should I water this plot today, and for how many minutes?". It reads a plot, its soil and its emitter from registry-service, reads the forecast from weather-service, and computes a day-by-day irrigation plan. It owns no data and has no database.

## Responsibilities

- Serve `GET /v1/plots/{id}/plan?days={1..7}` (default 7), starting today. Index 0 is today's recommendation.
- Compute every number with deterministic Python, following FAO-56 and the `irrigation-calc-reference` skill. No AI model is called at runtime.
- Propagate `stale` from the forecast to every affected day.
- Fail loudly when an upstream is down. It never returns a plan of zeros.

## Tech stack

Python, FastAPI, Pydantic v2, `pydantic-settings`, `httpx`, `uv`, pytest.

## Code layout

| File | Role |
|---|---|
| `main.py` | App, startup (reads settings once), `/health` |
| `config.py` | `Settings`: `REGISTRY_URL`, `WEATHER_URL` required; `UPSTREAM_TIMEOUT_SECONDS` default 10 |
| `routers/plan.py` | The one endpoint. Fetch plot, soil, emitter, forecast, then build the plan |
| `clients.py` | `Upstream`: HTTP calls to the two services. Any failure becomes `UpstreamUnavailable` naming the service |
| `schemas.py` | Strict upstream models (a string, null or NaN is an upstream failure, never a zero) and the `Plan` response |
| `crops.py` | Per-crop parameters: stage lengths, Kc values, root depth. Keyed by registry crop id |
| `irrigation.py` | Pure functions: Kc curve, ETc, bucket step, litres, run minutes. Also FAO-56 helpers such as TAW, Ks and adjusted p |
| `plan.py` | Loops over forecast days and assembles the response |
| `errors.py` | `application/problem+json` errors |
| `docs/research/fao56.md` | The FAO-56 research report behind the numbers |

## The calculation

For each forecast day:

1. **Season day** = days since planting + 1, clamped to the season length (after the season, Kc holds its end value).
2. **Kc** from the growth curve (FAO-56 Eq. 66): flat in the initial and mid stages, linear in development and late stages.
3. **ETc = Kc × ET0** (the crop's water use).
4. **Bucket capacity (TAW)** = soil available water (mm per metre) × root depth (m).
5. **Bucket step:** level = min(TAW, previous level + rain − ETc). If that is **below half of TAW**, irrigate back to full: `need_mm = TAW − level`. Exactly half does not trigger.
6. **Litres** = `need_mm × area_m2` (1 mm over 1 m² is 1 litre).
7. **Run minutes** = `need_mm / application_rate × 60`, where application rate (mm/h) = `flow_lph / (row_spacing_m × emitter_spacing_m)`.

Crop parameters (FAO-56 Tables 11, 12 and 22):

| Crop | Stages ini/dev/mid/late (days) | Kc ini / mid / end | Root depth |
|---|---|---|---|
| `tomato` | 30 / 40 / 45 / 30 | 0.6 / 1.15 / 0.80 | 0.7 m |
| `bell-pepper` | 30 / 35 / 40 / 20 | 0.6 / 1.05 / 0.90 | 0.5 m |

Nothing is rounded during the calculation. Output is rounded once: `kc` to 3 decimals, everything else to 2.

## API

```json
{
  "plot_id": "e0b5f3d2-6f40-4c7b-8d44-3f8a5b914004",
  "bucket_capacity_mm": 58.1,
  "trigger_mm": 29.05,
  "days": [
    {"date": "2026-06-01", "et0_mm": 5.0, "kc": 1.15, "need_mm": 0.0, "litres": 0.0,
     "run_minutes": 0.0, "stale": false, "bucket_end_mm": 52.35}
  ]
}
```

`bucket_end_mm` is the spec's "bucket level at end of day". `GET /health` returns `{"status": "ok"}`.

| Status | `code` | When |
|---|---|---|
| 422 | `VALIDATION` | `days` outside 1..7, malformed plot id, or a crop with no parameters |
| 404 | `NOT_FOUND` | unknown plot |
| 503 | `UPSTREAM_UNAVAILABLE` | registry or weather is unreachable, slow, returns non-200 or an unusable body. `detail` names the service. `Retry-After` is set |
| 500 | `INTERNAL` | a bug |

A stale forecast still produces a plan, with `stale: true` on every day. If the stale forecast has fewer days than requested, the plan is shorter.

## Request flow

1. Validate `days`.
2. `GET registry /v1/plots/{id}`. A 404 becomes `404 NOT_FOUND`. Anything else wrong becomes `503`.
3. `GET registry /v1/soils/{soil_id}` and `/v1/emitters/{emitter_id}`.
4. `GET weather /v1/forecast` using the plot's `lat` and `lon`.
5. `build_plan(...)` returns the plan.

Calls are sequential and synchronous. Each uses `UPSTREAM_TIMEOUT_SECONDS`.

## Configuration

| Variable | Meaning |
|---|---|
| `REGISTRY_URL` | Base URL of registry-service (required) |
| `WEATHER_URL` | Base URL of weather-service (required) |
| `UPSTREAM_TIMEOUT_SECONDS` | Timeout per upstream call (default 10) |

A missing URL stops startup with the variable named.

## Tests

79 tests with both upstreams faked: bucket logic, Kc curve, soil formulas, the plan endpoint, config and every upstream failure mode. Accuracy target NFR-2.5 is 0.5% against the reference values and the hand-calculated cases in the `irrigation-calc-reference` skill.

## Assumptions and open decisions

- **The bucket starts full today.** The service is stateless and the registry holds no soil moisture, so the real starting level is unknown. The effect is that today's answer is nearly always "No irrigation" and the first watering appears a few days out. This answers the grower's core question wrongly for a dry plot. The proposed fix is a documented, configurable starting level in `.env`, plus an optional override on the endpoint. This needs a decision.
- **Run times can exceed 24 hours.** Half of a 58 mm bucket on 1 mm/h emitters is about 30 hours. The plan reports it as calculated, with no cap.
- **Plots past the end of the season** (all four seed plots) use the crop's end Kc.
- **Simplifications:** no Ks stress factor and no p adjustment in the plan loop (irrigation triggers before stress), no wind or humidity correction of Kc, no drip scaling of Kc ini, no runoff or capillary rise.
- `irrigation.py` also holds the fuller FAO-56 daily step (`daily_soil_step`, with Ks and adjusted p) that the plan loop does not use. Keep it only if it backs the reference cases in the skill.
