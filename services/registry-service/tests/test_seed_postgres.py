import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
import sqlalchemy
from sqlalchemy import text

import db
import seed_registry_pg
from seed_registry_pg import TABLES, DatabaseNotEmpty, seed

pytestmark = pytest.mark.postgres_only

EXPECTED_COUNTS = {"plots": 4, "farms": 2, "crops": 2, "soils": 3, "emitters": 4}


@pytest.fixture
def pg_url() -> str:
    url = os.environ["TEST_DATABASE_URL"]
    name = sqlalchemy.engine.make_url(url).database
    assert "test" in name, f"refusing to drop tables in {name!r}"
    return url


@pytest.fixture
def pg(pg_url: str) -> Iterator[sqlalchemy.Connection]:
    engine = sqlalchemy.create_engine(db.sqlalchemy_url(pg_url))
    drop = text(f"DROP TABLE IF EXISTS {', '.join(TABLES)} CASCADE")
    with engine.connect() as conn:
        conn.execute(drop)
        conn.commit()
        yield conn
        conn.rollback()
        conn.execute(drop)
        conn.commit()
    engine.dispose()


def test_seed_creates_tables_with_expected_rows(pg: sqlalchemy.Connection) -> None:
    seed(pg)
    for table, expected in EXPECTED_COUNTS.items():
        count = pg.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()
        assert count == expected, table


def test_seed_matches_sqlite_seed(pg: sqlalchemy.Connection, seeded_db: Path) -> None:
    seed(pg)
    with sqlite3.connect(seeded_db) as lite:
        for table in TABLES:
            expected = lite.execute(f"SELECT * FROM {table} ORDER BY id").fetchall()
            actual = pg.execute(text(f"SELECT * FROM {table} ORDER BY id")).fetchall()
            assert [tuple(r) for r in actual] == expected, table


def test_second_seed_refuses_and_keeps_data(pg: sqlalchemy.Connection) -> None:
    seed(pg)
    pg.execute(text("INSERT INTO farms (id, name) VALUES ('extra', 'Extra farm')"))
    pg.commit()
    with pytest.raises(DatabaseNotEmpty) as excinfo:
        seed(pg)
    assert "farms" in str(excinfo.value)
    pg.rollback()
    assert pg.execute(text("SELECT name FROM farms WHERE id = 'extra'")).scalar_one() == (
        "Extra farm"
    )
    assert pg.execute(text("SELECT count(*) FROM farms")).scalar_one() == 3


def test_main_refuses_seeded_database(
    pg: sqlalchemy.Connection,
    pg_url: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    seed(pg)
    pg.commit()
    monkeypatch.setenv("DATABASE_URL", pg_url)
    assert seed_registry_pg.main() == 1
    assert "farms" in capsys.readouterr().err
