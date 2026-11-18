# registry-service: overview

Port **8000**. The system of record for AgroPilot. It stores farms and plots and serves read-only catalogues of crops, soils and drip emitters. It knows nothing about weather or irrigation. Other services only read from it, over HTTP.

## Responsibilities

- CRUD for **farms** and **plots** (area, crop, planting date, soil, drip layout, GPS position).
- Read-only **catalogues**: crops, soils (available water in mm per metre of depth) and emitters (flow in L/h).
- Validate every write and keep references consistent (a plot cannot point to a missing farm, crop, soil or emitter).
- Run on **SQLite** on a laptop and **PostgreSQL** in production, chosen only by `DATABASE_URL`.

## Tech stack

Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 Core (no ORM) with the `sqlite3` and `psycopg` 3 drivers, `pydantic-settings`, `uv`, pytest, Locust.

## Code layout

| File | Role |
|---|---|
| `main.py` | Builds the app, resolves `DATABASE_URL` once at startup, serves `/health` |
| `config.py` | `Settings` (`pydantic-settings`) and `database_url()`: process environment first, then `.env`, then the default `registry.db`. Validates the scheme and fails fast |
| `db.py` | SQLAlchemy engines (autocommit, one connection per request); write transactions; reads the driver's error behind SQLAlchemy's to decide "unavailable" or "bug" |
| `repository.py` | All SQL, one function per query. Column names used in `UPDATE` are checked against a whitelist |
| `schemas.py` | Pydantic request and response models and field validation |
| `routers/` | `farms.py`, `plots.py`, `catalogues.py`: thin HTTP handlers |
| `errors.py` | RFC 9457 `application/problem+json` responses with stable `code` values |
| `seed_registry.sh` / `seed_registry_pg.py` | Build and seed SQLite and PostgreSQL |
| `docker-compose.test.yml` | Throwaway PostgreSQL for tests |

## API

| Resource | Endpoints |
|---|---|
| Farms | `POST`, `GET /v1/farms`; `GET`, `PATCH`, `DELETE /v1/farms/{id}`; `GET /v1/farms/{id}/area` (sum of plot areas) |
| Plots | `POST`, `GET /v1/plots[?farm_id=]`; `GET`, `PATCH`, `DELETE /v1/plots/{id}` |
| Catalogues | `GET /v1/crops`, `/v1/soils`, `/v1/emitters`, each with `/{id}` |
| Health | `GET /health` returns `{"status": "ok"}` |

Plot fields: `id`, `farm_id`, `name`, `area_m2`, `crop_id`, `planting_date`, `soil_id`, `row_spacing_m`, `emitter_spacing_m`, `emitter_id`, `lat`, `lon`.

## Behaviour worth knowing

- **Validation:** positive numbers, latitude and longitude ranges, planting date not in the future (UTC), no blank or NUL-containing text, names up to 255 characters. Unknown fields are rejected. `PATCH` fields are optional but never `null`.
- **Integrity:** plot names are unique per farm (`409 CONFLICT`). A farm with plots cannot be deleted (`409`). A plot referencing a missing record gets `422`.
- **Concurrency:** every write runs in a transaction that takes a write lock up front (`BEGIN IMMEDIATE` on SQLite, an advisory lock on PostgreSQL), so "check then write" cannot race.
- **Errors:** `422 VALIDATION`, `404 NOT_FOUND`, `409 CONFLICT`, `503 UNAVAILABLE` (database unreachable or busy, with `Retry-After`). Unexpected failures answer `500` with code `UNAVAILABLE`.
- **PostgreSQL limits:** connect timeout 5 s, lock wait 5 s, statement timeout 30 s. Credential errors are treated as a configuration bug (`500`), not an outage.
- **Cross-database sorting:** lists are ordered by name with the `C` collation on PostgreSQL so both databases return the same order.

## Configuration

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | `sqlite:///registry.db` or `postgresql://user:password@host:5432/registry`. Unset means `registry.db` next to the code. An empty value, a missing scheme or an unsupported scheme stops startup |

## Provisioning

- SQLite: `bash seed_registry.sh` (deletes and rebuilds `registry.db`).
- PostgreSQL: `DATABASE_URL=postgresql://... uv run python seed_registry_pg.py`. It creates the tables and seeds the same sample data. It never deletes anything: if a registry table already exists it exits without changes.

## Tests and performance

- `uv run pytest` runs 198 tests on SQLite. 12 PostgreSQL-only tests run when `TEST_DATABASE_URL` points at the throwaway database. A parity suite checks both backends behave the same.
- NFR-2.2 (GET p95 ≤ 100 ms at 10 req/s, Locust, 60 s): **40 ms on SQLite, 71 ms on PostgreSQL** (measured after the move to SQLAlchemy; SQLite was 20 ms before), 0 failures. The PostgreSQL figure is against a local Docker database. Most of it is opening a new connection per request, so a remote database may need a connection pool.

## Known gaps

- The provisioning command on PostgreSQL works against an *existing* database. It does not create the database itself.
