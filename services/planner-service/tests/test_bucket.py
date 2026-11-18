"""Planner bucket rules (skill: Planner-service plan rules, cases 4 and 5)."""

import pytest

from irrigation import application_rate_mm_h, bucket_day, litres, run_minutes

# Case 4 plot: sand 83 mm/m, Zr 0.7 m, 1500 m2, rows 1.5 m, emitters 0.4 m, 0.6 L/h.
TAW = 83 * 0.7
ETC = 1.15 * 5.0


def test_application_rate_from_spacing_and_flow():
    assert application_rate_mm_h(0.6, 1.5, 0.4) == pytest.approx(1.0)
    assert application_rate_mm_h(1.0, 1.5, 0.4) == pytest.approx(1.6667, rel=1e-4)


def test_case4_day1_irrigates_and_refills_to_full():
    day = bucket_day(level_prev=33, taw=TAW, rain=0, etc_mm=ETC)
    assert day.need_mm == pytest.approx(30.85)
    assert day.level_end == pytest.approx(58.1)
    assert litres(day.need_mm, 1500) == pytest.approx(46275)
    assert run_minutes(day.need_mm, 0.6, 1.5, 0.4) == pytest.approx(1851)


def test_case4_day2_does_not_irrigate():
    day = bucket_day(level_prev=TAW, taw=TAW, rain=0, etc_mm=ETC)
    assert day.need_mm == 0
    assert day.level_end == pytest.approx(52.35)
    assert run_minutes(day.need_mm, 0.6, 1.5, 0.4) == 0


def test_case5_rain_keeps_level_above_trigger():
    day = bucket_day(level_prev=40, taw=TAW, rain=12, etc_mm=ETC)
    assert day.need_mm == 0
    assert day.level_end == pytest.approx(46.25)


def test_rain_beyond_full_is_capped_at_taw():
    day = bucket_day(level_prev=TAW, taw=TAW, rain=50, etc_mm=ETC)
    assert day.level_end == pytest.approx(TAW)
    assert day.need_mm == 0


def test_level_exactly_at_trigger_does_not_irrigate():
    # "Below half" triggers; exactly half does not.
    day = bucket_day(level_prev=TAW / 2 + ETC, taw=TAW, rain=0, etc_mm=ETC)
    assert day.need_mm == 0
    assert day.level_end == pytest.approx(TAW / 2)


def test_just_below_trigger_irrigates():
    day = bucket_day(level_prev=TAW / 2 + ETC - 0.01, taw=TAW, rain=0, etc_mm=ETC)
    assert day.need_mm == pytest.approx(TAW / 2 + 0.01)
    assert day.level_end == pytest.approx(TAW)


def test_seven_day_example_from_the_task():
    # 70 mm bucket losing 7 mm/day: days 1-5 reach exactly half, day 6 irrigates.
    level = 70.0
    needs = []
    for _ in range(6):
        day = bucket_day(level_prev=level, taw=70.0, rain=0, etc_mm=7.0)
        needs.append(day.need_mm)
        level = day.level_end
    assert needs[:5] == [0, 0, 0, 0, 0]
    assert needs[5] == pytest.approx(42.0)  # level 28 after ET, refilled to 70
