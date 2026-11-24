"""Planner bucket rules (skill: Planner-service plan rules, cases 4 and 5)."""

import pytest

from irrigation import application_rate_mm_h, bucket_day, effective_rain, litres, run_minutes

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


def test_empty_bucket_floors_level_so_need_is_exactly_taw():
    # Empty bucket (level 0), ETc 5.75. Not a soil_state start any more: dry is at the trigger.
    day = bucket_day(0.0, TAW, 0.0, ETC)
    assert day.need_mm == pytest.approx(TAW)
    assert day.level_end == pytest.approx(TAW)


def test_empty_bucket_with_et_larger_than_taw_still_needs_exactly_taw():
    assert bucket_day(0.0, TAW, 0.0, 100.0).need_mm == pytest.approx(TAW)


def test_empty_bucket_rain_is_counted():
    assert bucket_day(0.0, TAW, 40.0, ETC).level_end == pytest.approx(34.25)


def test_empty_bucket_rain_beyond_full_is_capped_at_taw():
    day = bucket_day(0.0, TAW, 100.0, ETC)
    assert day.need_mm == 0.0
    assert day.level_end == pytest.approx(TAW)


# Daily cap: a refill is spread over days, at most max_apply_mm a day (24 h of run time).
CAP = 24.0
ETC_4 = 4.0  # Kc end 0.80 x ET0 5.0


def test_refill_is_capped_per_day_and_keeps_going():
    day = bucket_day(0.0, TAW, 0.0, ETC_4, max_apply_mm=CAP)
    assert day.need_mm == pytest.approx(24.0)
    assert day.level_end == pytest.approx(24.0)
    assert day.refilling is True


def test_refill_continues_next_day_even_when_level_is_below_trigger_still():
    day = bucket_day(24.0, TAW, 0.0, ETC_4, max_apply_mm=CAP, refilling=True)
    assert day.need_mm == pytest.approx(24.0)  # level 20 + 24
    assert day.level_end == pytest.approx(44.0)
    assert day.refilling is True


def test_last_refill_day_applies_only_what_is_missing():
    day = bucket_day(44.0, TAW, 0.0, ETC_4, max_apply_mm=CAP, refilling=True)
    assert day.need_mm == pytest.approx(18.1)
    assert day.level_end == pytest.approx(TAW)
    assert day.refilling is False


def test_refill_continues_above_the_trigger():
    day = bucket_day(35.0, TAW, 0.0, ETC_4, max_apply_mm=CAP, refilling=True)  # level 31 > 29.05
    assert day.need_mm == pytest.approx(24.0)
    assert day.level_end == pytest.approx(55.0)


def test_rain_that_fills_the_bucket_ends_the_refill():
    day = bucket_day(44.0, TAW, 100.0, ETC_4, max_apply_mm=CAP, refilling=True)
    assert day.need_mm == 0.0
    assert day.level_end == pytest.approx(TAW)
    assert day.refilling is False


def test_no_cap_by_default_refills_in_one_day():
    day = bucket_day(0.0, TAW, 0.0, ETC_4)
    assert day.need_mm == pytest.approx(TAW)
    assert day.refilling is False


def test_rain_below_a_fifth_of_et0_is_ignored():
    # FAO-56 Ch. 8: rain below about 0.2 x ET0 is usually ignored (skill case 3: 0.6 mm at ET0 4).
    assert effective_rain(0.6, 4.0) == 0.0


def test_rain_at_or_above_a_fifth_of_et0_counts_in_full():
    assert effective_rain(0.8, 4.0) == pytest.approx(0.8)
    assert effective_rain(25.0, 4.0) == pytest.approx(25.0)
