# Registry SQLAlchemy Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every query in `services/registry-service` goes through SQLAlchemy, and its settings come from `pydantic-settings`, with no change in behaviour.

**Architecture:** SQLAlchemy Core (no ORM). One `Engine` per database URL, in autocommit mode, so `write_transaction` keeps issuing its own `BEGIN IMMEDIATE` (SQLite) or `BEGIN` plus advisory lock (PostgreSQL), exactly as today. `repository.py` keeps its function names and signatures and runs `text()` statements with named parameters. Error classification unwraps `exc.orig` from SQLAlchemy's wrapped exceptions.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.x (Core), `psycopg` 3 as the PostgreSQL driver, `pydantic-settings`, pytest.

**Spec:** [docs/superpowers/specs/2026-11-16-sqlalchemy-migration-design.md](../specs/2026-11-16-sqlalchemy-migration-design.md)

All paths are relative to `services/registry-service/`. Run commands from that folder.

## Global Constraints

- Behaviour does not change: same status codes, `code` values, `Retry-After: 5` on 503, same response bodies.
- `DATABASE_URL` is the only switch between SQLite and PostgreSQL (`sqlite:///...`, `postgresql://...`, `postgres://...`).
- SQLite opens with `mode=rw` (a missing file is a 503, never created) and `PRAGMA foreign_keys = ON` on every connection.
- PostgreSQL keeps: connect timeout `PG_CONNECT_TIMEOUT_SECONDS = 5`, `PG_LOCK_TIMEOUT = "5s"`, `PG_STATEMENT_TIMEOUT = "30s"`, advisory lock key `PG_WRITE_LOCK_KEY`, and `COLLATE "C"` ordering.
- Bad credentials stay a 500. Unreachable, missing database, timeouts, deadlocks and serialization failures stay 503.
- Lists stay ordered by `name, id`. The `UPDATE` column whitelist stays.
- No ORM models, no Alembic, no pool tuning, no router or `schemas.py` changes.
- Tests: 181 pass on SQLite and 12 PostgreSQL-only tests pass against `docker-compose.test.yml`. Assertions of existing tests do not change. Only the way they open connections may.

## Review Focus

- A plot name or farm name containing `:`, `%` or `?` (for example `"Block A:1 100%?"`) is stored and returned unchanged, because `text()` must bind it rather than parse it.
- Two concurrent `POST /v1/plots` with the same name on one farm give exactly one 201 and one 409.
- After a request fails with 409 or 422, the next write on a new request succeeds, so no connection keeps the write lock.
- A missing SQLite file is a 503 and the file is still absent afterwards.
- Bad PostgreSQL credentials are a 500 even though SQLAlchemy wraps the error as `OperationalError`.

---

### Task 1: Settings through pydantic-settings, and commit the design

**Files:**
- Modify: `config.py`, `pyproject.toml`, `uv.lock`
- Test: `tests/test_config.py` (existing, plus one new test)

**Interfaces:**
- Produces: `config.database_url(env_file: Path = ENV_FILE) -> str` (same signature and `ValueError` messages as today), `config.SERVICE_DIR`, `config.DEFAULT_SQLITE_URL`, and `config.Settings` (a `pydantic_settings.BaseSettings` with `database_url: str`, env name `DATABASE_URL`).

- [ ] **Step 1: Add the new test** in `tests/test_config.py`: `test_settings_class_reads_database_url_from_the_environment` sets `DATABASE_URL=sqlite:///x.db` with `monkeypatch.setenv` and asserts `config.Settings(_env_file=None).database_url == "sqlite:///x.db"`.
- [ ] **Step 2: Run** `uv run pytest tests/test_config.py -q`. Expected: the new test FAILS (`Settings` missing).
- [ ] **Step 3: Add dependencies** with `uv add sqlalchemy pydantic-settings`. Leave `python-dotenv` for now.
- [ ] **Step 4: Rewrite `config.py`** around `class Settings(BaseSettings)`. Process environment beats `.env` (the library default), and a set-but-empty variable counts as set. A validator on `database_url` raises `ValueError` with the three existing messages (`empty DATABASE_URL; unset it to use registry.db`, `DATABASE_URL has no scheme; ...`, `Unsupported DATABASE_URL scheme: 'mysql'`). `database_url(env_file)` builds `Settings(_env_file=env_file)` and re-raises a pydantic `ValidationError` as a plain `ValueError` carrying only the original message (never the URL, since it may hold a password). The default is `DEFAULT_SQLITE_URL`.
- [ ] **Step 5: Run** `uv run pytest tests/test_config.py -q`. Expected: all pass, with no edit to existing assertions.
- [ ] **Step 6: Remove `python-dotenv`** (`uv remove python-dotenv`) only if `grep -rn dotenv --include=*.py .` finds nothing left. Run `uv run pytest -q` (181 pass, 12 skipped).
- [ ] **Step 7: Commit** the design document, this plan, and the settings change:

```bash
git add docs/superpowers services/registry-service/config.py services/registry-service/pyproject.toml services/registry-service/uv.lock services/registry-service/tests/test_config.py
git commit -m "feat(registry): read settings with pydantic-settings; add SQLAlchemy design and plan"
```

---

### Task 2: The SQLAlchemy engine and error classifiers, alongside the old code

Additive: nothing existing changes, so the suite stays green.

**Files:**
- Modify: `db.py`
- Test: `tests/test_engine.py` (new)

**Interfaces:**
- Consumes: `config.SERVICE_DIR`.
- Produces in `db.py`:
  - `sqlalchemy_url(url: str) -> str`: `postgresql://` and `postgres://` become `postgresql+psycopg://`. `sqlite:///relative` resolves against `SERVICE_DIR`. SQLite URLs get `?mode=rw&uri=true` form (`sqlite:///file:/abs/path.db?mode=rw&uri=true`).
  - `engine_for(url: str, lock_timeout: str, statement_timeout: str) -> sqlalchemy.Engine`: cached with `functools.cache`, so the timeouts are part of the key. `poolclass=NullPool`, `isolation_level="AUTOCOMMIT"`. SQLite: a `connect` event runs `PRAGMA foreign_keys = ON`. PostgreSQL: `connect_args={"connect_timeout": PG_CONNECT_TIMEOUT_SECONDS, "options": f"-c lock_timeout={lock_timeout} -c statement_timeout={statement_timeout}"}`.
  - `connect_url(url: str) -> sqlalchemy.Connection`: calls `engine_for(url, PG_LOCK_TIMEOUT, PG_STATEMENT_TIMEOUT).connect()`. The module constants are read at call time, because tests monkeypatch them.
  - `connect(path: Path = DB_PATH) -> sqlalchemy.Connection`: SQLite file shortcut for tests.
  - `underlying(exc: Exception) -> Exception`: returns `exc.orig` for a `sqlalchemy.exc.DBAPIError`, else `exc`.
  - `is_unavailable`, `is_unique_violation`, `is_foreign_key_violation`: now call `underlying(exc)` first, then apply today's logic. They must still accept raw `sqlite3` and `psycopg` errors, because `tests/test_errors.py` passes those in directly.
- Name clashes: the old `connect` and `connect_url` still return old connections until Task 3. Add the new ones as `engine_for` and `sa_connect` now, and rename them in Task 3.

- [ ] **Step 1: Write failing tests** in `tests/test_engine.py`:
  - `test_sqlalchemy_url_maps_postgres_schemes` (`postgres://u:p@h/d` and `postgresql://u:p@h/d` both give `postgresql+psycopg://u:p@h/d`).
  - `test_sqlite_connection_has_foreign_keys_on` (`sa_connect` to a seeded file, `PRAGMA foreign_keys` returns 1; mark `sqlite_only`).
  - `test_missing_sqlite_file_is_not_created` (`sa_connect` on `tmp_path/"x.db"` raises `OperationalError` and the file is absent; `sqlite_only`).
  - `test_wrapped_sqlite_busy_is_unavailable`: wrap a `sqlite3.OperationalError` with `sqlite_errorname = "SQLITE_BUSY"` in `sqlalchemy.exc.OperationalError(None, None, orig)` and assert `is_unavailable(...)` is true. Same for `SQLITE_CONSTRAINT_UNIQUE` with `is_unique_violation` on a wrapped `IntegrityError`.
- [ ] **Step 2: Run** `uv run pytest tests/test_engine.py -q`. Expected: FAIL (names missing).
- [ ] **Step 3: Implement** the interfaces above in `db.py`. For PostgreSQL credential failures, SQLAlchemy wraps `psycopg.OperationalError` with no SQLSTATE, so the existing `PG_CREDENTIAL_ERRORS` message check applies to `str(underlying(exc))`.
- [ ] **Step 4: Run** `uv run pytest -q`. Expected: all green (181 pass, 12 skipped).
- [ ] **Step 5: Commit** `git commit -am "feat(registry): add SQLAlchemy engine and error classifiers"` (include `tests/test_engine.py`).

---

### Task 3: Switch repository, routers and error handlers to SQLAlchemy (SQLite)

**Files:**
- Modify: `db.py`, `repository.py`, `errors.py`, `routers/farms.py`, `routers/plots.py`, `routers/catalogues.py`, `main.py`, `tests/support.py`, `tests/conftest.py`, `tests/test_errors.py`, `tests/test_constraints.py`
- Test: whole suite, plus `tests/test_sql_safety.py` (new)

**Interfaces:**
- Consumes: Task 2's `engine_for`, `underlying`, classifiers.
- Produces:
  - `db.Conn = sqlalchemy.Connection`; `db.connect_url(url) -> Conn` and `db.connect(path) -> Conn` (the Task 2 `sa_connect` renamed; the old implementations and `PgConnection`, `_PLACEHOLDER` are deleted).
  - `db.write_transaction(conn: Conn)`: unchanged behaviour. SQLite runs `BEGIN IMMEDIATE`. PostgreSQL runs `BEGIN` then `SELECT pg_advisory_xact_lock(PG_WRITE_LOCK_KEY)`. All through `conn.exec_driver_sql`. Rollback on any exception when a transaction is open (SQLite: `conn.connection.dbapi_connection.in_transaction`; PostgreSQL: `info.transaction_status` as today). Then `COMMIT`.
  - `db.INTEGRITY_ERRORS = (sqlalchemy.exc.IntegrityError,)`.
  - `db.order_by_name(conn: Conn) -> str`: uses `conn.dialect.name == "postgresql"` instead of `isinstance`.
  - `repository` functions: same names, parameters and return types as today. Every query becomes `conn.execute(text(sql), params)` with named parameters (`:farm_id`), and rows are read with `.mappings()` and returned as `dict`.
  - `errors.register_error_handlers` registers `_handle_database_error` for `sqlalchemy.exc.DBAPIError` (instead of `sqlite3.Error` and `psycopg.Error`). It calls `is_unavailable(exc)` and logs the same messages.
  - `main.py`: still resolves the URL once in `lifespan` through `config.database_url()`.

- [ ] **Step 1: Write the safety tests** in `tests/test_sql_safety.py` (they pass on the old code too, so they pin behaviour):
  - `test_names_with_sql_looking_characters_round_trip(client)`: create a farm named `"Block A:1 100%?"`, create a plot with that name on it, `GET` both, assert the names are unchanged.
  - `test_next_write_works_after_a_conflict(client)`: create a plot, create the same name again (409), then create a different name (201).
  - `test_concurrent_creates_with_same_name_give_one_201_and_one_409(client)`: two threads post the same plot; assert sorted statuses `[201, 409]`. Run once, and mark `sqlite_only` if the `TestClient` is not thread-safe enough; otherwise leave it for both backends.
- [ ] **Step 2: Run** `uv run pytest tests/test_sql_safety.py -q`. Expected: PASS on the old code (this is the baseline).
- [ ] **Step 3: Update `db.py`** as in Interfaces; delete `PgConnection`, `_PLACEHOLDER`, the `sqlite3`/`psycopg` connection code, and the `Conn` union. Keep every constant. `get_db` yields `connect_url(request.app.state.database_url)` and closes it.
- [ ] **Step 4: Rewrite `repository.py`** over `text()`. Keep `_rows`, `_row`, `_update` (whitelist check unchanged; `UPDATE` assignments become `column = :column` with the id as `:_id`). `delete_farm`, `insert_plot` and `update_plot` keep catching `INTEGRITY_ERRORS` and mapping through the classifiers.
- [ ] **Step 5: Update `errors.py`** handler registration as in Interfaces; remove the `sqlite3` and `psycopg` imports it no longer needs.
- [ ] **Step 6: Update routers** only where they import removed names (`Conn`, `DbConn` stay valid). `routers/plots.py` and `routers/farms.py` should need no logic change.
- [ ] **Step 7: Update tests' connection helpers only.** `tests/support.py`: `database_from(path)` and `database_from_url(url)` yield `connect(path)` and `connect_url(url)`. `tests/test_errors.py`: the impatient SQLite fixture sets the busy timeout with `conn.exec_driver_sql("PRAGMA busy_timeout = 50")`; the raw `sqlite3` blocker may stay (it simulates another client). `tests/test_constraints.py`: wrap its SQL in `text()`. No assertion changes.
- [ ] **Step 8: Run** `uv run pytest -q`. Expected: 181 pass plus the new tests, 12 skipped. If `test_locked_database_returns_503_with_retry_after` or the missing-file test fails, the cause is SQLite's transaction mode: confirm the engine is `AUTOCOMMIT` and `BEGIN IMMEDIATE` is issued through `exec_driver_sql`.
- [ ] **Step 9: Commit** `git commit -am "refactor(registry): run all queries through SQLAlchemy"`.

---

### Task 4: PostgreSQL seeder and PostgreSQL tests on SQLAlchemy

**Files:**
- Modify: `seed_registry_pg.py`, `tests/conftest.py`, `tests/test_seed_postgres.py`, `tests/test_postgres_errors.py`, `tests/test_backend_parity.py` (only if it opens connections)

**Interfaces:**
- Consumes: Task 3's `db.sqlalchemy_url`, `db.connect_url`.
- Produces: `seed_registry_pg.seed(conn: sqlalchemy.Connection) -> None` (same behaviour: refuses with `DatabaseNotEmpty` if any of `TABLES` exists, otherwise creates and seeds the 15 rows). `main()` builds a plain engine from `db.sqlalchemy_url(config.database_url())` and calls `seed` inside `engine.begin()`. `TABLES`, `DatabaseNotEmpty` and the `SCHEMA_AND_SEED` text are unchanged.

- [ ] **Step 1: Start PostgreSQL:** `docker compose -f docker-compose.test.yml up -d --wait`, then `export TEST_DATABASE_URL=postgresql://registry:registry@localhost:55432/registry_test`.
- [ ] **Step 2: Run** `uv run pytest -q`. Expected: PostgreSQL-backed tests that use `seed` or `PgConnection` fail (the baseline for this task).
- [ ] **Step 3: Update `seed_registry_pg.py`:** existing-table check through `sqlalchemy.inspect(conn).get_table_names()` filtered by `TABLES`; run `SCHEMA_AND_SEED` with `conn.exec_driver_sql`; row counts with `text()`.
- [ ] **Step 4: Update test fixtures:** in `conftest.py`, the `db_url` fixture drops and re-seeds through an engine (`sqlalchemy.create_engine(db.sqlalchemy_url(url))` and `engine.begin()`), and takes the database name from `sqlalchemy.engine.make_url(url).database`. In `test_seed_postgres.py`, the `pg` fixture yields a SQLAlchemy connection and queries use `text()`. In `test_postgres_errors.py`, `test_every_connection_has_lock_and_statement_timeouts` reads `SHOW lock_timeout` through `conn.execute(text(...)).scalar()`. The raw `psycopg` blockers and killers in that file may stay; they act as other clients. `kill_then_insert` reads the backend pid with `conn.execute(text("SELECT pg_backend_pid()")).scalar()`.
- [ ] **Step 5: Run** `uv run pytest -q` with `TEST_DATABASE_URL` set. Expected: everything passes, including the PostgreSQL-only tests, with the SQLite-only ones skipped.
- [ ] **Step 6: Run** `uv run pytest -q` without it. Expected: 181 pass plus the new tests, 12 skipped.
- [ ] **Step 7: Run the seeder by hand** against an empty database to prove FR-2.2: `DATABASE_URL=postgresql://registry:registry@localhost:55432/registry_seed_check uv run python seed_registry_pg.py` after creating that database. Expected output: a line with the counts `4 plots, 2 farms, 2 crops, 3 soils, 4 emitters` (15 rows). A second run exits 1 with "Nothing was changed."
- [ ] **Step 8: Commit** `git commit -am "refactor(registry): seed and test PostgreSQL through SQLAlchemy"`.

---

### Task 5: Performance check and documentation

**Files:**
- Modify: `README.md`, `OVERVIEW.md` (registry service), `../../docs/project-overview.md`, `../../README.md` (only if it mentions the drivers)

- [ ] **Step 1: Measure.** Start the service on SQLite and on PostgreSQL and run the existing Locust file (`scripts/locustfile.py`) at 10 requests per second for 60 s on each, as the README describes. Expected: GET p95 at most 100 ms on both, 0 failures. If PostgreSQL exceeds 100 ms, report the number and stop; do not add a pool without asking.
- [ ] **Step 2: Update docs.** Registry `OVERVIEW.md`: remove the "Known gaps against the P2 spec" section's SQLAlchemy and `pydantic-settings` items; change the tech stack and code layout rows for `db.py` and `repository.py`; update the p95 figures with the new measurements. Registry `README.md`: same stack line and figures. `docs/project-overview.md`: §4 tech stack and §5 architecture say SQLAlchemy Core instead of "no ORM / raw sqlite3 and psycopg", and §11 "Why no ORM?" explains that Core keeps the SQL visible while meeting the SQLAlchemy requirement.
- [ ] **Step 3: Check for stale references:** `grep -rn "sqlite3\|PgConnection\|python-dotenv" --include=*.md . ../../docs ../../README.md`. Expected: only mentions that are still true (the SQLite file, the `sqlite3` CLI used by `seed_registry.sh`).
- [ ] **Step 4: Full run** `uv run pytest -q` on SQLite and with `TEST_DATABASE_URL`. Expected: green both ways.
- [ ] **Step 5: Commit** `git commit -am "docs(registry): record the SQLAlchemy migration and new measurements"`.
