import sqlite3
from pathlib import Path
from types import SimpleNamespace

import psycopg
import pytest
import sqlalchemy
from psycopg.pq import TransactionStatus
from sqlalchemy import exc

import db


def test_sqlalchemy_url_maps_postgres_schemes():
    assert db.sqlalchemy_url("postgres://u:p@h/d") == "postgresql+psycopg://u:p@h/d"
    assert db.sqlalchemy_url("postgresql://u:p@h/d") == "postgresql+psycopg://u:p@h/d"


@pytest.mark.sqlite_only
def test_sqlite_connection_has_foreign_keys_on(seeded_db: Path):
    conn = db.connect(seeded_db)
    try:
        assert conn.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
    finally:
        conn.close()


@pytest.mark.sqlite_only
def test_missing_sqlite_file_is_not_created(tmp_path: Path):
    with pytest.raises(exc.OperationalError):
        db.connect(tmp_path / "x.db")

    assert not (tmp_path / "x.db").exists()


def wrapped(error_class, name: str, wrapper):
    orig = error_class("x")
    orig.sqlite_errorname = name
    return wrapper(None, None, orig)


def test_wrapped_sqlite_busy_is_unavailable():
    assert db.is_unavailable(wrapped(sqlite3.OperationalError, "SQLITE_BUSY", exc.OperationalError))


def test_wrapped_sqlite_unique_violation_is_detected():
    error = wrapped(sqlite3.IntegrityError, "SQLITE_CONSTRAINT_UNIQUE", exc.IntegrityError)

    assert db.is_unique_violation(error)
    assert not db.is_foreign_key_violation(error)


def test_wrapped_sqlite_foreign_key_violation_is_detected():
    error = wrapped(sqlite3.IntegrityError, "SQLITE_CONSTRAINT_FOREIGNKEY", exc.IntegrityError)

    assert db.is_foreign_key_violation(error)


def test_engine_is_cached_per_url_and_timeouts(tmp_path: Path):
    url = f"sqlite:///{tmp_path / 'a.db'}"

    first = db.engine_for(url, "5s", "30s")

    assert isinstance(first, sqlalchemy.Engine)
    assert db.engine_for(url, "5s", "30s") is first
    assert db.engine_for(url, "100ms", "30s") is not first


@pytest.mark.sqlite_only
@pytest.mark.parametrize("folder", ["a#b", "q?x", "p%41"])
def test_sqlite_path_with_special_characters_opens_the_existing_file(
    seeded_db: Path, tmp_path: Path, folder: str
):
    target = tmp_path / folder
    target.mkdir()
    (target / "registry.db").write_bytes(seeded_db.read_bytes())

    conn = db.connect(target / "registry.db")
    try:
        assert conn.exec_driver_sql("SELECT count(*) FROM farms").scalar() == 2
    finally:
        conn.close()


@pytest.mark.sqlite_only
@pytest.mark.parametrize("folder", ["a#b", "q?x"])
def test_missing_sqlite_file_in_special_folder_is_not_created(tmp_path: Path, folder: str):
    (tmp_path / folder).mkdir()

    with pytest.raises(exc.OperationalError):
        db.connect(tmp_path / folder / "x.db")

    assert sorted(p.name for p in tmp_path.iterdir()) == [folder]
    assert list((tmp_path / folder).iterdir()) == []


@pytest.mark.sqlite_only
def test_database_errors_do_not_expose_bound_parameters(seeded_db: Path):
    conn = db.connect(seeded_db)
    try:
        with pytest.raises(exc.IntegrityError) as caught:
            conn.execute(
                sqlalchemy.text("INSERT INTO farms (id, name) VALUES (:id, :name)"),
                {"id": "b7e2c0a0-3c1d-4f0a-9a11-0c5d2e6f1001", "name": "SECRET-NAME"},
            )
    finally:
        conn.close()

    assert "SECRET-NAME" not in str(caught.value)


class FakeConn:
    """Stands in for a SQLAlchemy connection so Postgres-only code runs without a server."""

    def __init__(self, dialect="postgresql", invalidated=False, transaction_status=None):
        self.dialect = SimpleNamespace(name=dialect)
        self.invalidated = invalidated
        info = SimpleNamespace(transaction_status=transaction_status)
        self.connection = SimpleNamespace(dbapi_connection=SimpleNamespace(info=info))
        self.statements = []

    def exec_driver_sql(self, sql):
        self.statements.append(sql)


def test_invalidated_connection_is_not_in_a_transaction():
    assert db._in_transaction(FakeConn(invalidated=True)) is False


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (TransactionStatus.INTRANS, True),
        (TransactionStatus.INERROR, True),
        (TransactionStatus.IDLE, False),
    ],
)
def test_postgres_transaction_state_comes_from_libpq(status, expected):
    assert db._in_transaction(FakeConn(transaction_status=status)) is expected


def test_postgres_write_transaction_takes_the_advisory_lock_then_commits():
    conn = FakeConn()

    with db.write_transaction(conn):
        pass

    assert conn.statements == [
        "BEGIN",
        f"SELECT pg_advisory_xact_lock({db.PG_WRITE_LOCK_KEY})",
        "COMMIT",
    ]


def test_write_transaction_rolls_back_and_reraises_when_the_block_fails():
    conn = FakeConn(transaction_status=TransactionStatus.INERROR)

    with pytest.raises(RuntimeError, match="boom"), db.write_transaction(conn):
        raise RuntimeError("boom")

    assert conn.statements[-1] == "ROLLBACK"
    assert "COMMIT" not in conn.statements


def test_write_transaction_skips_rollback_when_the_connection_is_gone():
    conn = FakeConn(invalidated=True)

    with pytest.raises(RuntimeError, match="boom"), db.write_transaction(conn):
        raise RuntimeError("boom")

    assert "ROLLBACK" not in conn.statements


def test_errors_that_are_not_database_errors_are_not_unavailable():
    assert db.is_unavailable(ValueError("not a database error")) is False


def test_postgres_unique_violation_is_recognised():
    assert db.is_unique_violation(psycopg.errors.UniqueViolation()) is True
    assert db.is_unique_violation(psycopg.errors.ForeignKeyViolation()) is False


def test_postgres_foreign_key_violation_is_recognised():
    assert db.is_foreign_key_violation(psycopg.errors.ForeignKeyViolation()) is True
    assert db.is_foreign_key_violation(psycopg.errors.UniqueViolation()) is False


def test_postgres_sorts_names_with_the_c_collation():
    assert db.order_by_name(FakeConn()) == 'ORDER BY name COLLATE "C", id COLLATE "C"'
    assert db.order_by_name(FakeConn(dialect="sqlite")) == "ORDER BY name, id"


def test_sqlite_url_without_three_slashes_is_rejected():
    with pytest.raises(ValueError, match="must start with sqlite:///"):
        db.sqlalchemy_url("sqlite:registry.db")


def test_unrecognised_url_scheme_is_passed_through():
    assert db.sqlalchemy_url("mysql://u:p@h/d") == "mysql://u:p@h/d"


def test_postgres_engine_sets_timeouts_and_autocommit(monkeypatch):
    created = {}

    def fake_create_engine(url, **kwargs):
        created.update(url=url, **kwargs)
        return "engine"

    monkeypatch.setattr(sqlalchemy, "create_engine", fake_create_engine)

    # __wrapped__ skips the cache, so the fake engine is not kept for later tests.
    engine = db.engine_for.__wrapped__("postgresql://u:p@h/d", "2s", "9s")

    assert engine == "engine"
    assert created["url"] == "postgresql+psycopg://u:p@h/d"
    assert created["isolation_level"] == "AUTOCOMMIT"
    assert created["connect_args"] == {
        "connect_timeout": db.PG_CONNECT_TIMEOUT_SECONDS,
        "options": "-c lock_timeout=2s -c statement_timeout=9s",
    }
