import sqlite3
from types import SimpleNamespace

import pytest
from sqlalchemy import exc
from support import FARM_DEMO, PLOT_EAST, PLOT_NORTH, UNKNOWN_ID
from test_errors import assert_problem

import db
import repository
from errors import ConflictProblem


def integrity_error(sqlite_errorname):
    orig = sqlite3.IntegrityError("constraint failed")
    orig.sqlite_errorname = sqlite_errorname
    return exc.IntegrityError("DELETE FROM farms", {}, orig)


def test_update_rejects_columns_outside_the_whitelist(db_url):
    conn = db.connect_url(db_url)
    try:
        with pytest.raises(ValueError, match=r"unexpected columns for farms: \['bogus'\]"):
            repository.update_farm(conn, FARM_DEMO, {"bogus": 1})
    finally:
        conn.close()


def test_unrecognised_plot_error_is_reraised_unchanged():
    error = ValueError("not a constraint problem")

    with pytest.raises(ValueError) as raised:
        repository._raise_plot_problem(error)

    assert raised.value is error


def test_delete_farm_reraises_integrity_errors_that_are_not_foreign_keys():
    error = integrity_error("SQLITE_CONSTRAINT_NOTNULL")

    def failing_execute(*args, **kwargs):
        raise error

    conn = SimpleNamespace(execute=failing_execute)

    with pytest.raises(exc.IntegrityError) as raised:
        repository.delete_farm(conn, FARM_DEMO)

    assert raised.value is error


def test_delete_farm_turns_a_foreign_key_failure_into_a_conflict():
    def failing_execute(*args, **kwargs):
        raise integrity_error("SQLITE_CONSTRAINT_FOREIGNKEY")

    with pytest.raises(ConflictProblem, match="Farm still has plots"):
        repository.delete_farm(SimpleNamespace(execute=failing_execute), FARM_DEMO)


def test_patch_name_lost_race_is_still_a_409(client, monkeypatch):
    # Another request takes the name between the route's check and the UPDATE: only the
    # database's UNIQUE(farm_id, name) is left to stop it. Skip the check to simulate that.
    monkeypatch.setattr("routers.plots._check_name_free", lambda *args, **kwargs: None)

    response = client.patch(f"/v1/plots/{PLOT_EAST}", json={"name": "North block"})

    body = assert_problem(response, 409, "CONFLICT")
    assert body["detail"] == "A plot with this name already exists on this farm"


def test_patch_reference_deleted_mid_request_is_still_a_422(client, monkeypatch):
    # The referenced record disappears after the route's check: only the foreign key is left.
    monkeypatch.setattr("routers.plots._check_references", lambda *args, **kwargs: None)

    response = client.patch(f"/v1/plots/{PLOT_NORTH}", json={"farm_id": UNKNOWN_ID})

    body = assert_problem(response, 422, "VALIDATION")
    assert body["detail"] == (
        "farm_id, crop_id, soil_id, or emitter_id refers to a record that does not exist"
    )
