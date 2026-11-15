import pytest

from irrigation import (
    Stages,
    climate_adjusted_kc,
    drip_kc_ini,
    etc,
    kc_for_day,
)

# Mediterranean tomato, Table 11: 30/40/45/30 days.
MED = Stages(ini=30, dev=40, mid=45, late=30)


def test_case1_kc_curve_development_day_50():
    kc = kc_for_day(50, MED, kc_ini=0.6, kc_mid=1.15, kc_end=0.8)
    assert kc == pytest.approx(0.875, abs=1e-9)
    assert etc(kc, 5.0) == pytest.approx(4.375, abs=1e-9)


def test_kc_flat_in_initial_and_mid_stages():
    assert kc_for_day(1, MED, 0.6, 1.15, 0.8) == 0.6
    assert kc_for_day(30, MED, 0.6, 1.15, 0.8) == 0.6
    assert kc_for_day(71, MED, 0.6, 1.15, 0.8) == 1.15
    assert kc_for_day(115, MED, 0.6, 1.15, 0.8) == 1.15


def test_kc_late_stage_declines_to_kc_end():
    # day 130 is 15 days into a 30-day late stage: halfway from 1.15 to 0.8
    assert kc_for_day(130, MED, 0.6, 1.15, 0.8) == pytest.approx(0.975)
    assert kc_for_day(145, MED, 0.6, 1.15, 0.8) == pytest.approx(0.8)


def test_kc_day_outside_season_rejected():
    with pytest.raises(ValueError):
        kc_for_day(0, MED, 0.6, 1.15, 0.8)
    with pytest.raises(ValueError):
        kc_for_day(146, MED, 0.6, 1.15, 0.8)


def test_case2_climate_adjustment_kc_mid():
    kc_mid = climate_adjusted_kc(1.15, u2=3, rhmin=35, h=0.6)
    assert kc_mid == pytest.approx(1.199, abs=5e-4)
    assert etc(kc_mid, 5.0) == pytest.approx(5.997, abs=5e-3)


def test_climate_adjustment_zero_at_reference_climate_h3():
    assert climate_adjusted_kc(1.15, u2=2, rhmin=45, h=3) == pytest.approx(1.15)


def test_kc_end_below_045_not_adjusted():
    assert climate_adjusted_kc(0.40, u2=4, rhmin=30, h=0.6, end=True) == 0.40
    assert climate_adjusted_kc(0.70, u2=4, rhmin=30, h=0.6, end=True) > 0.70


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(u2=0.9, rhmin=45, h=0.6),
        dict(u2=6.1, rhmin=45, h=0.6),
        dict(u2=2, rhmin=19.9, h=0.6),
        dict(u2=2, rhmin=80.1, h=0.6),
        dict(u2=2, rhmin=45, h=0.05),
        dict(u2=2, rhmin=45, h=10.5),
    ],
)
def test_climate_adjustment_out_of_range_rejected(kwargs):
    with pytest.raises(ValueError):
        climate_adjusted_kc(1.15, **kwargs)


def test_drip_scales_kc_ini_by_fw():
    assert drip_kc_ini(0.6, fw=0.4) == pytest.approx(0.24)
