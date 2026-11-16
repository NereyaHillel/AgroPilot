from typing import Any, NoReturn

from sqlalchemy import text

from db import (
    INTEGRITY_ERRORS,
    Conn,
    is_foreign_key_violation,
    is_unique_violation,
    order_by_name,
)
from errors import ConflictProblem, ValidationProblem

Row = dict[str, Any]

FARM_COLUMNS = frozenset({"name"})
PLOT_COLUMNS = frozenset(
    {
        "farm_id",
        "name",
        "area_m2",
        "crop_id",
        "planting_date",
        "soil_id",
        "row_spacing_m",
        "emitter_spacing_m",
        "emitter_id",
        "lat",
        "lon",
    }
)
# No stored id can contain NUL, and Postgres rejects it in a query parameter, so a catalogue id
# with NUL is simply not found on either backend.
_NUL = "\x00"
_PLOT_SELECT = (
    "SELECT id, farm_id, name, area_m2, crop_id, planting_date, soil_id, "
    "row_spacing_m, emitter_spacing_m, emitter_id, lat, lon FROM plots"
)


def _rows(conn: Conn, sql: str, params: Row | None = None) -> list[Row]:
    return [dict(row) for row in conn.execute(text(sql), params or {}).mappings()]


def _row(conn: Conn, sql: str, params: Row) -> Row | None:
    row = conn.execute(text(sql), params).mappings().first()
    return None if row is None else dict(row)


def _update(conn: Conn, table: str, columns: frozenset[str], row_id: str, changes: Row) -> None:
    if not changes:
        return
    if not set(changes) <= columns:
        raise ValueError(f"unexpected columns for {table}: {sorted(set(changes) - columns)}")
    # Column names are interpolated, so they are checked against the whitelist above.
    assignments = ", ".join(f"{column} = :{column}" for column in changes)
    conn.execute(text(f"UPDATE {table} SET {assignments} WHERE id = :_id"), {**changes, "_id": row_id})


def _raise_plot_problem(exc: Exception) -> NoReturn:
    if is_unique_violation(exc):
        raise ConflictProblem("A plot with this name already exists on this farm") from exc
    if is_foreign_key_violation(exc):
        raise ValidationProblem(
            "farm_id, crop_id, soil_id, or emitter_id refers to a record that does not exist"
        ) from exc
    raise exc


def list_farms(conn: Conn) -> list[Row]:
    return _rows(conn, f"SELECT id, name FROM farms {order_by_name(conn)}")


def get_farm(conn: Conn, farm_id: str) -> Row | None:
    return _row(conn, "SELECT id, name FROM farms WHERE id = :id", {"id": farm_id})


def insert_farm(conn: Conn, farm: Row) -> None:
    conn.execute(text("INSERT INTO farms (id, name) VALUES (:id, :name)"), farm)


def update_farm(conn: Conn, farm_id: str, changes: Row) -> None:
    _update(conn, "farms", FARM_COLUMNS, farm_id, changes)


def count_plots(conn: Conn, farm_id: str) -> int:
    sql = text("SELECT COUNT(*) FROM plots WHERE farm_id = :farm_id")
    return conn.execute(sql, {"farm_id": farm_id}).scalar_one()


def total_plot_area(conn: Conn, farm_id: str) -> float:
    sql = text("SELECT COALESCE(SUM(area_m2), 0) FROM plots WHERE farm_id = :farm_id")
    return float(conn.execute(sql, {"farm_id": farm_id}).scalar_one())


def delete_farm(conn: Conn, farm_id: str) -> None:
    try:
        conn.execute(text("DELETE FROM farms WHERE id = :id"), {"id": farm_id})
    except INTEGRITY_ERRORS as exc:
        if is_foreign_key_violation(exc):
            raise ConflictProblem("Farm still has plots; delete its plots first") from exc
        raise


def list_plots(conn: Conn, farm_id: str | None) -> list[Row]:
    if farm_id is None:
        return _rows(conn, f"{_PLOT_SELECT} {order_by_name(conn)}")
    return _rows(conn, f"{_PLOT_SELECT} WHERE farm_id = :farm_id {order_by_name(conn)}", {"farm_id": farm_id})


def get_plot(conn: Conn, plot_id: str) -> Row | None:
    return _row(conn, f"{_PLOT_SELECT} WHERE id = :id", {"id": plot_id})


def plot_name_taken(conn: Conn, farm_id: str, name: str, plot_id: str | None) -> bool:
    sql = "SELECT 1 FROM plots WHERE farm_id = :farm_id AND name = :name"
    params: Row = {"farm_id": farm_id, "name": name}
    if plot_id is not None:
        sql += " AND id != :plot_id"
        params["plot_id"] = plot_id
    return conn.execute(text(sql), params).first() is not None


def insert_plot(conn: Conn, plot: Row) -> None:
    try:
        conn.execute(
            text(
                "INSERT INTO plots (id, farm_id, name, area_m2, crop_id, planting_date, soil_id, "
            "row_spacing_m, emitter_spacing_m, emitter_id, lat, lon) VALUES "
            "(:id, :farm_id, :name, :area_m2, :crop_id, :planting_date, :soil_id, "
            ":row_spacing_m, :emitter_spacing_m, :emitter_id, :lat, :lon)"
            ),
            plot,
        )
    except INTEGRITY_ERRORS as exc:
        _raise_plot_problem(exc)


def update_plot(conn: Conn, plot_id: str, changes: Row) -> None:
    try:
        _update(conn, "plots", PLOT_COLUMNS, plot_id, changes)
    except INTEGRITY_ERRORS as exc:
        _raise_plot_problem(exc)


def delete_plot(conn: Conn, plot_id: str) -> None:
    conn.execute(text("DELETE FROM plots WHERE id = :id"), {"id": plot_id})


def list_crops(conn: Conn) -> list[Row]:
    return _rows(conn, f"SELECT id, name FROM crops {order_by_name(conn)}")


def get_crop(conn: Conn, crop_id: str) -> Row | None:
    if _NUL in crop_id:
        return None
    return _row(conn, "SELECT id, name FROM crops WHERE id = :id", {"id": crop_id})


def list_soils(conn: Conn) -> list[Row]:
    return _rows(
        conn, f"SELECT id, name, available_water_mm_per_m FROM soils {order_by_name(conn)}"
    )


def get_soil(conn: Conn, soil_id: str) -> Row | None:
    if _NUL in soil_id:
        return None
    return _row(
        conn,
        "SELECT id, name, available_water_mm_per_m FROM soils WHERE id = :id",
        {"id": soil_id},
    )


def list_emitters(conn: Conn) -> list[Row]:
    return _rows(conn, f"SELECT id, name, flow_lph FROM emitters {order_by_name(conn)}")


def get_emitter(conn: Conn, emitter_id: str) -> Row | None:
    if _NUL in emitter_id:
        return None
    return _row(conn, "SELECT id, name, flow_lph FROM emitters WHERE id = :id", {"id": emitter_id})
