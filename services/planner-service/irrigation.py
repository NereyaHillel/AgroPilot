"""Daily irrigation calculation engine, FAO-56 single-Kc method (Ch. 5, 6, 8).

Units: depths mm; ET0/ETc mm/day; Zr, h m; theta m3/m3; u2 m/s; RHmin %.
Capillary rise (CR) is taken as 0. Nothing is rounded.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Stages:
    """Stage lengths in days (FAO-56 Table 11)."""

    ini: int
    dev: int
    mid: int
    late: int


@dataclass(frozen=True)
class CropPreset:
    """Values verified in FAO-56 Tables 12 and 22.

    Kc ini, Kc end, stage lengths and Zr (pick inside zr_range) are NOT
    presets: the caller must supply them.
    """

    kc_mid: float
    h: float
    p: float
    zr_range: tuple[float, float]


CROPS = {
    "tomato": CropPreset(kc_mid=1.15, h=0.6, p=0.40, zr_range=(0.7, 1.5)),
    "bell_pepper": CropPreset(kc_mid=1.05, h=0.7, p=0.30, zr_range=(0.5, 1.0)),
}


def etc(kc: float, et0: float) -> float:
    """ETc = Kc x ET0 (Eq. 56/58)."""
    return kc * et0


def kc_for_day(day: int, stages: Stages, kc_ini: float, kc_mid: float, kc_end: float) -> float:
    """Kc on a season day (Eq. 66); flat in initial/mid, linear in dev/late.

    Day is 1-based and used directly as `i` in Eq. 66, so day == stages.ini is
    the last initial day. The source does not fix the day-1 convention.
    Days outside 1..total season length raise ValueError.
    """
    end_ini = stages.ini
    end_dev = end_ini + stages.dev
    end_mid = end_dev + stages.mid
    end_late = end_mid + stages.late
    if not 1 <= day <= end_late:
        raise ValueError(f"day must be within 1..{end_late}, got {day}")
    if day <= end_ini:
        return kc_ini
    if day <= end_dev:
        return kc_ini + (day - end_ini) / stages.dev * (kc_mid - kc_ini)
    if day <= end_mid:
        return kc_mid
    return kc_mid + (day - end_mid) / stages.late * (kc_end - kc_mid)


def climate_adjusted_kc(kc_tab: float, u2: float, rhmin: float, h: float, end: bool = False) -> float:
    """Eq. 62 (Kc mid) or, with end=True, Eq. 65 (Kc end).

    Kc end below 0.45 is returned unchanged (Eq. 65 applies only at >= 0.45).
    Ranges per Ch. 6: 1 <= u2 <= 6, 20 <= RHmin <= 80, 0.1 <= h <= 10.
    (Source prints 0.1 < h < 10; bounds are treated as inclusive here.)
    """
    if not 1 <= u2 <= 6:
        raise ValueError(f"u2 must be within 1..6 m/s, got {u2}")
    if not 20 <= rhmin <= 80:
        raise ValueError(f"RHmin must be within 20..80 %, got {rhmin}")
    if not 0.1 <= h <= 10:
        raise ValueError(f"h must be within 0.1..10 m, got {h}")
    if end and kc_tab < 0.45:
        return kc_tab
    return kc_tab + (0.04 * (u2 - 2) - 0.004 * (rhmin - 45)) * (h / 3) ** 0.3


def drip_kc_ini(kc_ini: float, fw: float) -> float:
    """Kc ini under partial wetting = fw x Kc ini (Eq. 60). Only Kc ini is scaled."""
    return fw * kc_ini


def taw(theta_fc: float, theta_wp: float, zr: float) -> float:
    """Total available water, mm (Eq. 82)."""
    return 1000 * (theta_fc - theta_wp) * zr


def adjusted_p(p_table: float, etc_mm: float) -> float:
    """p = p(Table 22) + 0.04 (5 - ETc), clamped to 0.1..0.8 (Ch. 8, used in Eq. 83)."""
    return min(max(p_table + 0.04 * (5 - etc_mm), 0.1), 0.8)


def ks_factor(dr: float, taw: float, p: float) -> float:
    """Water stress coefficient (Eq. 84): 1 if Dr <= RAW, else (TAW-Dr)/((1-p) TAW)."""
    if dr <= p * taw:  # RAW = p x TAW (Eq. 83)
        return 1.0
    return (taw - dr) / ((1 - p) * taw)


@dataclass(frozen=True)
class SoilDay:
    etc: float      # unstressed ETc, mm/day
    p: float        # ETc-adjusted p
    raw: float      # mm (Eq. 83)
    ks: float
    etc_adj: float  # stressed ETc, mm/day (Eq. 81)
    dr: float       # end-of-day depletion, mm
    dp: float       # deep percolation, mm


def daily_soil_step(
    dr_prev: float, taw: float, p_table: float, kc: float, et0: float,
    rain: float, runoff: float, irrigation: float,
) -> SoilDay:
    """One day of the root-zone bucket (Eq. 81-88).

    Conventions (as in the skill's case 3): p is adjusted with the unstressed
    ETc (Kc x ET0); Ks uses start-of-day depletion (dr_prev). Rain and
    irrigation are treated as arriving before ET, so DP uses the stressed ETc.
    """
    etc_full = etc(kc, et0)
    p = adjusted_p(p_table, etc_full)
    raw = p * taw
    ks = ks_factor(dr_prev, taw, p)
    etc_adj = ks * etc_full  # Eq. 81
    net_water = (rain - runoff) + irrigation
    dr = dr_prev - net_water + etc_adj  # Eq. 85, CR = DP = 0 before clamp
    dr = min(max(dr, 0.0), taw)  # Eq. 86
    dp = max(net_water - etc_adj - dr_prev, 0.0)  # Eq. 88
    return SoilDay(etc_full, p, raw, ks, etc_adj, dr, dp)


def irrigation_decision(dr_end: float, raw: float) -> float:
    """Net irrigation (mm) for the next morning: refill to field capacity.

    Triggers when end-of-day depletion exceeds RAW; the amount equals that
    depletion. Rule is the Annex 8 summary, not a verified equation.
    """
    return dr_end if dr_end > raw else 0.0


# --- Planner-service plan rules (skill: "Planner-service plan rules") ---------


TRIGGER_FRACTION = 0.5  # irrigate when the level would fall below this share of the bucket
# Share of the bucket that is full at the start of day 1, as chosen by the farmer.
START_FRACTION = {"dry": 0.0, "half": 0.5, "wet": 1.0}


@dataclass(frozen=True)
class BucketDay:
    need_mm: float   # net irrigation, mm; 0 on a day without irrigation
    level_end: float  # water in the bucket at the end of the day, mm


def bucket_day(level_prev: float, taw: float, rain: float, etc_mm: float) -> BucketDay:
    """One plan day. Irrigate when the level would fall below half of TAW.

    Level after rain and ET is capped at TAW (excess drains) and floored at 0
    (a dry start cannot lose more water than it holds). If it is below
    0.5 x TAW, the irrigation refills the bucket to TAW. Exactly half does not
    trigger. No Ks and no p adjustment: irrigation happens before stress.
    """
    level_pre = max(0.0, min(taw, level_prev + rain - etc_mm))
    if level_pre < TRIGGER_FRACTION * taw:
        return BucketDay(need_mm=taw - level_pre, level_end=taw)
    return BucketDay(need_mm=0.0, level_end=level_pre)


def application_rate_mm_h(flow_lph: float, row_spacing_m: float, emitter_spacing_m: float) -> float:
    """Drip application rate: flow / (row spacing x emitter spacing), mm/h."""
    return flow_lph / (row_spacing_m * emitter_spacing_m)


def litres(need_mm: float, area_m2: float) -> float:
    """1 mm over 1 m2 is 1 litre."""
    return need_mm * area_m2


def run_minutes(need_mm: float, flow_lph: float, row_spacing_m: float, emitter_spacing_m: float) -> float:
    """Minutes to apply need_mm at the plot's application rate."""
    return need_mm / application_rate_mm_h(flow_lph, row_spacing_m, emitter_spacing_m) * 60
