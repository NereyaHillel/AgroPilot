"""Per-crop plan parameters, decided with the user (skill: Planner-service plan rules).

Stage lengths: FAO-56 Table 11. Kc: Table 12 (Kc ini is the Solanum group value
0.6 because the per-crop cell is blank; tomato Kc end is the midpoint of 0.70-0.90).
Zr: smaller end of the Table 22 range, which FAO-56 advises for scheduling.
"""

from dataclasses import dataclass

from irrigation import Stages


@dataclass(frozen=True)
class CropPlan:
    stages: Stages
    kc_ini: float
    kc_mid: float
    kc_end: float
    zr_m: float


# Keys are registry-service crop ids.
CROP_PLANS = {
    # Table 11 "Mediterranean, Apr/May" row.
    "tomato": CropPlan(Stages(30, 40, 45, 30), kc_ini=0.6, kc_mid=1.15, kc_end=0.80, zr_m=0.7),
    # Table 11 "Europe and Mediterranean, Apr/Jun" row; initial stage printed "25/30", 30 matches the 125 d total.
    "bell-pepper": CropPlan(Stages(30, 35, 40, 20), kc_ini=0.6, kc_mid=1.05, kc_end=0.90, zr_m=0.5),
}
