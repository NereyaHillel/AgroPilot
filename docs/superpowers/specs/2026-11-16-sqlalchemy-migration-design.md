# Registry service: move data access to SQLAlchemy

Short design. Approved in conversation on 2026-11-16.

## Intent and why

The P2 spec says "All data access goes through SQLAlchemy" and "each Python service reads its settings with pydantic-settings, in one `config.py`". The registry uses raw `sqlite3` and `psycopg` behind a small adapter (`PgConnection`), and reads `DATABASE_URL` with `python-dotenv`. This change closes both gaps. Behaviour must not change.

## Goals

- Every query in `services/registry-service` runs through SQLAlchemy, including `seed_registry_pg.py` and the test helpers that talk to PostgreSQL.
- `DATABASE_URL` is still the only switch between SQLite and PostgreSQL. No code change to move between them (NFR-2.1).
- `config.py` uses `pydantic-settings` and still fails fast with a clear error on a bad value.
- All 181 SQLite tests pass without edits to their assertions. The 12 PostgreSQL-only tests pass against a throwaway PostgreSQL.

## Non-goals

- No ORM models, no Alembic, no new endpoints, no schema change.
- No connection pooling work beyond what the engine does by default.
- No change to routers, `schemas.py`, `errors.py` response shapes, or status codes.

## Anti-goals (a failure even if tests pass)

- Losing the write lock taken before the checks (`BEGIN IMMEDIATE` on SQLite, `pg_advisory_xact_lock` on PostgreSQL).
- A database error that used to be a 503 becoming a 500, or the reverse. Bad credentials stay a 500.
- A missing SQLite file silently creating an empty database (`mode=rw` must stay).
- The two databases ordering lists differently (PostgreSQL keeps the `C` collation).

## Approaches considered

1. **SQLAlchemy Core with SQL kept close to today's (chosen).** `repository.py` keeps its function signatures and builds the same queries with `text()` or Core. The routers and tests barely notice. Trade-off: less "SQLAlchemy-flavoured" than the ORM, but it is the smallest change that meets "all data access goes through SQLAlchemy".
2. **SQLAlchemy ORM with mapped models.** Idiomatic, but adds model classes, session handling and loading rules for five fixed tables, and every router and test that expects plain dicts would change. Rejected as more risk for no gain.
3. **Keep the raw drivers and document the exception.** Cheapest, but does not meet the spec. Rejected.

## Design

- `db.py`: build one `Engine` from `DATABASE_URL` at startup (`sqlite:///...` and `postgresql://...`, which SQLAlchemy needs as `postgresql+psycopg://`). SQLite: open with `mode=rw`, turn `PRAGMA foreign_keys = ON` on each connection, use autocommit-style control so `BEGIN IMMEDIATE` works. PostgreSQL: keep the 5 s connect timeout, 5 s lock timeout and 30 s statement timeout. `get_db` still yields one connection per request. `write_transaction` keeps taking the write lock first.
- Error classification (`is_unavailable`, `is_unique_violation`, `is_foreign_key_violation`) reads the original driver error from SQLAlchemy's `OperationalError` and `IntegrityError` (`exc.orig`), with the same SQLite error names and PostgreSQL SQLSTATEs as today.
- `repository.py`: same functions and signatures, rewritten over SQLAlchemy. The column whitelist for `UPDATE` stays.
- `seed_registry_pg.py` and the PostgreSQL test fixtures use SQLAlchemy.
- `config.py`: a `Settings` class (`pydantic-settings`) with `DATABASE_URL`, reading the environment first and `.env` second, defaulting to `registry.db`. Empty value, missing scheme and unsupported scheme still stop startup.
- `pyproject.toml`: add `sqlalchemy` and `pydantic-settings`. Drop `python-dotenv` only if nothing else uses it. Keep `psycopg` as SQLAlchemy's PostgreSQL driver.

## Verification

- `uv run pytest` on SQLite: 181 pass, 12 skipped, as today.
- PostgreSQL tests through `docker-compose.test.yml` with `TEST_DATABASE_URL`: the 12 run and the whole suite passes.
- Re-measure GET p95 on SQLite and PostgreSQL (NFR-2.2) with the existing Locust file, and update the registry README and `OVERVIEW.md`, which currently name the SQLAlchemy gap.

## Left to the builder

- Exact SQLAlchemy construction (`text()` versus Core expressions) per query.
- How to keep SQLite in manual-transaction mode with the SQLite driver.
- Whether `python-dotenv` can be removed.
