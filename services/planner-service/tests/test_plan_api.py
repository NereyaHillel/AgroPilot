import pytest

from conftest import PLOT_ID, assert_problem, forecast_days

DAY_FIELDS = {"date", "et0_mm", "kc", "need_mm", "litres", "run_minutes", "stale", "bucket_end_mm"}


def get_plan(client, days=None, plot_id=PLOT_ID, soil_state="wet"):
    params = {"soil_state": soil_state}
    if days is not None:
        params["days"] = days
    return client.get(f"/v1/plots/{plot_id}/plan", params=params)


def test_seven_day_plan_matches_hand_calculation(client):
    # Hand-checked: tomato Kc mid 1.15 x ET0 5.0 = 5.75 mm/day; TAW 58.1 mm (sand 83 x 0.7 m);
    # trigger 29.05 mm; bucket starts full. Level hits 23.6 on day 6, so need 34.5 mm,
    # 51 750 L, and 34.5 mm / 1.0 mm/h = 2070 min.
    response = get_plan(client)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"plot_id", "bucket_capacity_mm", "trigger_mm", "days"}
    assert body["plot_id"] == PLOT_ID
    assert body["bucket_capacity_mm"] == 58.1  # sand 83 mm/m x 0.7 m
    assert body["trigger_mm"] == 29.05  # irrigate when the level would fall below this
    days = body["days"]
    assert len(days) == 7
    assert all(set(day) == DAY_FIELDS for day in days)
    assert [day["date"] for day in days][0] == "2026-06-01"
    assert [day["kc"] for day in days] == [1.15] * 7
    assert [day["need_mm"] for day in days] == [0, 0, 0, 0, 0, 34.5, 0]
    assert [day["run_minutes"] for day in days] == [0, 0, 0, 0, 0, 2070.0, 0]
    assert days[5]["litres"] == 51750.0
    assert [day["bucket_end_mm"] for day in days] == [52.35, 46.6, 40.85, 35.1, 29.35, 58.1, 52.35]
    assert all(day["stale"] is False for day in days)


def test_days_defaults_to_7_and_is_sent_to_weather(client, world):
    get_plan(client)
    assert world.weather_requests[0]["days"] == "7"
    assert world.weather_requests[0]["lat"] == "31.4"


def test_days_shortens_the_plan(client, world):
    response = get_plan(client, days=3)
    assert len(response.json()["days"]) == 3
    assert world.weather_requests[0]["days"] == "3"


@pytest.mark.parametrize("days", ["0", "8", "-1", "abc", "2.5", ""])
def test_bad_days_is_422_validation(client, days):
    body = assert_problem(get_plan(client, days=days), 422, "VALIDATION")
    assert "days" in body["detail"]


def test_malformed_plot_id_is_422(client):
    assert_problem(get_plan(client, plot_id="not-a-uuid"), 422, "VALIDATION")


def test_unknown_plot_is_404_not_found(client, world):
    other = "00000000-0000-4000-8000-000000000000"
    assert_problem(get_plan(client, plot_id=other), 404, "NOT_FOUND")


def test_rain_reduces_need_and_caps_the_bucket(client, world):
    world.forecast["days"] = forecast_days(2, rain=100.0)
    days = get_plan(client, days=2).json()["days"]
    assert [day["bucket_end_mm"] for day in days] == [58.1, 58.1]
    assert [day["need_mm"] for day in days] == [0, 0]


def test_run_time_follows_emitter_flow_and_spacing(client, world):
    # 1.0 L/h on 1.5 x 0.4 m = 1.6667 mm/h; 34.5 mm takes 34.5 / 1.6667 x 60 = 1242 min.
    world.emitter["flow_lph"] = 1.0
    day6 = get_plan(client).json()["days"][5]
    assert day6["need_mm"] == 34.5
    assert day6["run_minutes"] == 1242.0


def test_stale_forecast_marks_every_day_stale(client, world):
    world.forecast["stale"] = True
    days = get_plan(client).json()["days"]
    assert len(days) == 7
    assert all(day["stale"] is True for day in days)


def test_stale_forecast_with_fewer_days_gives_a_shorter_plan(client, world):
    world.forecast["stale"] = True
    world.forecast["days"] = forecast_days(4)
    days = get_plan(client, days=7).json()["days"]
    assert len(days) == 4
    assert all(day["stale"] is True for day in days)


def test_kc_follows_the_growth_curve(client, world):
    # Tomato planted on day 1 = FIRST_DAY: day 1 initial stage, Kc ini 0.6 (Eq. 66, flat).
    world.plot["planting_date"] = "2026-06-01"
    days = get_plan(client, days=3).json()["days"]
    assert [day["kc"] for day in days] == [0.6, 0.6, 0.6]


def test_kc_holds_kc_end_after_the_season(client, world):
    world.plot["planting_date"] = "2025-01-01"
    assert get_plan(client, days=1).json()["days"][0]["kc"] == 0.8


def test_bell_pepper_uses_its_own_parameters(client, world):
    # Pepper: Zr 0.5 m, so TAW = 41.5; mid-season Kc 1.05; day 100 is in the late stage.
    world.plot["crop_id"] = "bell-pepper"
    world.plot["planting_date"] = "2026-06-01"
    body = get_plan(client, days=1).json()
    assert body["days"][0]["kc"] == 0.6
    assert body["days"][0]["bucket_end_mm"] == 41.5 - 0.6 * 5.0


def test_crop_without_parameters_is_422(client, world):
    world.plot["crop_id"] = "wheat"
    assert_problem(get_plan(client), 422, "VALIDATION")


def test_soil_state_is_required(client):
    assert_problem(client.get(f"/v1/plots/{PLOT_ID}/plan"), 422, "VALIDATION")


@pytest.mark.parametrize("value", ["", "full", "DRY", "0.5"])
def test_unknown_soil_state_is_422(client, value):
    body = assert_problem(get_plan(client, soil_state=value), 422, "VALIDATION")
    assert "soil_state" in body["detail"]


def test_dry_start_irrigates_on_day_1(client):
    day1 = get_plan(client, soil_state="dry").json()["days"][0]
    assert (day1["need_mm"], day1["litres"], day1["run_minutes"], day1["bucket_end_mm"]) == (
        58.1, 87150.0, 3486.0, 58.1,
    )


def test_half_start_irrigates_on_day_1(client):
    # level 29.05 - ETc 5.75 = 23.3 < trigger 29.05, so need 34.8 mm
    day1 = get_plan(client, soil_state="half").json()["days"][0]
    assert (day1["need_mm"], day1["litres"], day1["run_minutes"]) == (34.8, 52200.0, 2088.0)
