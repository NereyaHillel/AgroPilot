import sqlite3
from pathlib import Path

import pytest
import sqlalchemy
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
