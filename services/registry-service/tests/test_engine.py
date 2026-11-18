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
