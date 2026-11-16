# registry-service

The system of record for AgroPilot: **farms** and **plots** (area, crop, planting date, soil, drip layout, GPS location), plus read-only catalogues of **crops**, **soils** and **drip emitters**. planner-service and the frontend read their data from here. Part of [AgroPilot](../../README.md).

## Tech stack

- Python 3.12, FastAPI, Pydantic v2
- SQLite (`registry.db`) by default, PostgreSQL in production (psycopg 3), chosen by `DATABASE_URL`
- [uv](https://docs.astral.sh/uv/) for dependencies
- pytest for tests, Locust for load tests

## Layout

```
routers/                  HTTP endpoints (farms, plots, catalogues)
schemas.py                Request/response models and validation
repository.py             SQL queries
db.py                     Connections and transactions
errors.py                 RFC 9457 error responses
config.py                 Reads DATABASE_URL
seed_registry.sh          Builds registry.db (SQLite) with sample data
seed_registry_pg.py       Creates and seeds the registry tables in PostgreSQL
docker-compose.test.yml   Throwaway PostgreSQL for tests
tests/                    pytest suite
scripts/                  Load test (Locust)
```

## Getting started

Requirements: Python 3.12 and `uv`. The `sqlite3` CLI is needed for the SQLite setup and for the default test run. Docker is needed only to run the tests against PostgreSQL.

```bash
cd services/registry-service
uv sync
bash seed_registry.sh          # creates registry.db (deletes any existing one)
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

- Health check: http://127.0.0.1:8000/health returns `{"status": "ok"}`
- Interactive API docs: http://127.0.0.1:8000/docs

To run the whole system instead, use `bash scripts/run-all.sh` from the repository root.

## Database

The service uses SQLite by default (`registry.db` next to the code) and PostgreSQL 12 or later in production. The `DATABASE_URL` setting chooses the database. It is read from the process environment first, then from a `.env` file in this folder (`.env` is gitignored). Supported URLs:

```
DATABASE_URL=sqlite:///registry.db
DATABASE_URL=postgresql://user:password@host:5432/registry
```

`.env.example` lists both styles; copy it to `.env` and keep one. Without `DATABASE_URL` the service uses `registry.db`. `DATABASE_URL` is read once at startup: an empty value, a value without a scheme or any other URL scheme stops the service with an error before it serves requests.

The API behaves the same on both databases, except for two limits added so that PostgreSQL can store every accepted value. Both apply on SQLite too:

- Text fields reject NUL characters with `422` (PostgreSQL text cannot hold them), and a catalogue id containing NUL answers `404`.
- Farm and plot names are at most 255 characters (`422` above that), which keeps them within PostgreSQL's index size limit.

To set up PostgreSQL, create the registry tables and sample data in an existing database with:

```bash
cd services/registry-service
DATABASE_URL=postgresql://user:password@host:5432/registry uv run python seed_registry_pg.py
```

The script never deletes anything: if any registry table already exists, it prints a message and exits without changing the database. When PostgreSQL is unreachable or busy (no connection within 5 s, a lock wait over 5 s, a statement over 30 s, deadlock, serialization failure) the API answers `503`; other unexpected database errors answer `500`. Both use the `UNAVAILABLE` code.

## API

| Resource | Endpoints |
| --- | --- |
| Farms | `POST` `GET` `/v1/farms` · `GET` `PATCH` `DELETE` `/v1/farms/{id}` · `GET` `/v1/farms/{id}/area` |
| Plots | `POST` `GET` `/v1/plots[?farm_id=]` · `GET` `PATCH` `DELETE` `/v1/plots/{id}` |
| Catalogues (read-only) | `GET` `/v1/crops`, `/v1/soils`, `/v1/emitters` and `/{id}` |

All errors use the [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) `application/problem+json` format with a `code` of `VALIDATION`, `NOT_FOUND`, `CONFLICT`, or `UNAVAILABLE`.

## Tests

```bash
cd services/registry-service
uv run pytest
```

Each test runs against a freshly seeded copy of the database, so `registry.db` is never modified. On SQLite 181 tests pass and the 12 PostgreSQL-only tests are skipped.

To run the suite against PostgreSQL, start the throwaway database and set `TEST_DATABASE_URL`:

```bash
cd services/registry-service
docker compose -f docker-compose.test.yml up -d --wait
TEST_DATABASE_URL=postgresql://registry:registry@localhost:55432/registry_test uv run pytest
```

Each test drops and reseeds the registry tables in that database, so the database name must contain `test`. Tests never use `DATABASE_URL`. Stop the database with `docker compose -f docker-compose.test.yml down`.

## Performance

`GET` requests must have a p95 latency of at most 100 ms at 10 requests per second. Measured with Locust on the seeded data: **p95 = 20 ms, 0 failures** on SQLite and **p95 = 76 ms, 0 failures** on PostgreSQL (60 s at 10 requests per second).

The PostgreSQL figure was measured against a database in a local Docker container. Most of it is the cost of opening a new connection for every request. A remote database, especially over TLS, adds network round trips to each of those connections, so latency there will be higher. If p95 exceeds 100 ms in that setup, the next step is a connection pool (`psycopg_pool`).

## More

- [../../docs/project-overview.md](../../docs/project-overview.md): what the registry does and how it is built
- [../../docs/judgment-log.md](../../docs/judgment-log.md): decisions made where the spec was open
