import pytest

from irrigation import (
    CROPS,
    adjusted_p,
    daily_soil_step,
    etc,
    irrigation_decision,
    ks_factor,
    taw,
)


def test_presets_only_verified_values():
    t, b = CROPS["tomato"], CROPS["bell_pepper"]
    assert (t.kc_mid, t.h, t.p, t.zr_range) == (1.15, 0.6, 0.40, (0.7, 1.5))
    assert (b.kc_mid, b.h, b.p, b.zr_range) == (1.05, 0.7, 0.30, (0.5, 1.0))
    assert not hasattr(t, "kc_end") and not hasattr(b, "kc_ini")


def test_case3_stress_day_pepper():
    pepper = CROPS["bell_pepper"]
    t_aw = taw(theta_fc=0.25, theta_wp=0.12, zr=0.5)
    assert t_aw == pytest.approx(65.0)

    r = daily_soil_step(
        dr_prev=25.0, taw=t_aw, p_table=pepper.p,
        kc=pepper.kc_mid, et0=5.0, rain=0.0, runoff=0.0, irrigation=0.0,
    )
    assert r.etc == pytest.approx(5.25)
    assert r.p == pytest.approx(0.29)
    assert r.raw == pytest.approx(18.85, abs=1e-6)
    assert r.ks == pytest.approx(0.867, abs=5e-4)
    assert r.etc_adj == pytest.approx(4.55, abs=5e-3)
    assert r.dr == pytest.approx(29.55, abs=5e-3)
    assert r.dp == 0.0
    assert irrigation_decision(r.dr, r.raw) == pytest.approx(29.55, abs=5e-3)


def test_rain_exceeding_depletion_clamps_to_zero_and_gives_dp():
    # TAW 100, p ~0.4 -> RAW ~40 > Dr_prev 10, so Ks = 1 and ETc adj = 4
    r = daily_soil_step(
        dr_prev=10.0, taw=100.0, p_table=0.4, kc=0.8, et0=5.0,
        rain=30.0, runoff=0.0, irrigation=0.0,
    )
    assert r.etc_adj == pytest.approx(4.0)
    assert r.dr == 0.0
    assert r.dp == pytest.approx(16.0)


def test_runoff_reduces_effective_rain():
    r = daily_soil_step(10.0, 100.0, 0.4, 0.8, 5.0, rain=30.0, runoff=10.0, irrigation=0.0)
    assert r.dp == pytest.approx(6.0)


def test_dr_clamped_to_taw():
    # tiny TAW so one day of (stressed) ETc overshoots it: 2.5 + 2.77 > 4
    r = daily_soil_step(2.5, 4.0, 0.3, 1.05, 5.0, 0.0, 0.0, 0.0)
    assert r.dr == 4.0


def test_ks_is_one_when_dr_at_or_below_raw():
    assert ks_factor(dr=18.85, taw=65.0, p=0.29) == 1.0
    assert ks_factor(dr=0.0, taw=65.0, p=0.29) == 1.0
    r = daily_soil_step(10.0, 65.0, 0.3, 1.05, 5.0, 0.0, 0.0, 0.0)
    assert r.ks == 1.0 and r.etc_adj == pytest.approx(r.etc)


def test_ks_zero_when_fully_depleted():
    assert ks_factor(dr=65.0, taw=65.0, p=0.3) == 0.0


def test_p_adjustment_and_clamping():
    assert adjusted_p(0.30, etc_mm=5.0) == pytest.approx(0.30)
    assert adjusted_p(0.30, etc_mm=5.25) == pytest.approx(0.29)
    assert adjusted_p(0.30, etc_mm=20.0) == 0.1   # 0.30 - 0.6 -> clamp low
    assert adjusted_p(0.70, etc_mm=0.0) == 0.8    # 0.70 + 0.2 -> clamp high


def test_irrigation_not_triggered_when_dr_at_or_below_raw():
    assert irrigation_decision(18.85, 18.85) == 0.0
    assert irrigation_decision(5.0, 18.85) == 0.0


def test_etc_is_kc_times_et0():
    assert etc(1.15, 5.0) == pytest.approx(5.75)
