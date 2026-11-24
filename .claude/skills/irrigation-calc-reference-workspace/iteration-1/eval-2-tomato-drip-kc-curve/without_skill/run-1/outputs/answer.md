# Tomato on drip: Kc on season days 20, 50 and 140

## Inputs

- **Stage lengths** (FAO-56 Table 11, tomato, "Mediterranean, Apr/May"): L_ini 30, L_dev 40, L_mid 45, L_late 30, so 145 days in total. These match `CROP_PLANS["tomato"]` in `services/planner-service/crops.py`.
  - Initial: days 1-30
  - Development: days 31-70
  - Mid-season: days 71-115
  - Late season: days 116-145
- **Table 12 values:** Kc ini = 0.60 (the Solanum group value, as in the repo), Kc mid = 1.15, Kc end = 0.80 (your choice, inside the 0.70-0.90 range). The maximum height is h = 0.6 m.
- **Climate:** u2 = 3 m/s and RHmin = 30 %. Both are inside the valid ranges for Eq. 62/65 (1-6 m/s, 20-80 %).
- **Drip:** wetted fraction fw = 0.35.
- **Day convention:** season day 1 is the planting date, and the day number i goes straight into Eq. 66. This is the convention `kc_for_day` uses.

## Step 1: Climate-adjusted Kc mid (Eq. 62)

Kc mid = Kc mid(Tab) + [0.04(u2 - 2) - 0.004(RHmin - 45)] (h/3)^0.3

- 0.04(3 - 2) = 0.040
- -0.004(30 - 45) = +0.060
- The bracket is 0.100.
- (0.6/3)^0.3 = 0.2^0.3 = 0.6170

**Kc mid = 1.15 + 0.100 x 0.6170 = 1.2117, rounded to 1.21.**

## Step 2: Climate-adjusted Kc end (Eq. 65)

Kc end(Tab) is 0.80, which is at least 0.45, so the same adjustment applies:

**Kc end = 0.80 + 0.100 x 0.6170 = 0.8617, rounded to 0.86.**

## Step 3: Kc ini under drip (Eq. 60)

Kc ini = fw x Kc ini = 0.35 x 0.60 = **0.21**

## Step 4: The Kc on each day (Eq. 66)

Eq. 66 is Kc_i = Kc_prev + [(i - ΣL_prev) / L_stage] (Kc_next - Kc_prev).

| Season day | Stage | Calculation | Kc |
|---|---|---|---|
| 20 | Initial (1-30) | Flat at Kc ini | **0.21** |
| 50 | Development (31-70) | 0.21 + (50 - 30)/40 x (1.2117 - 0.21) = 0.21 + 0.5 x 1.0017 | **0.71** (0.7109) |
| 140 | Late (116-145) | 1.2117 + (140 - 115)/30 x (0.8617 - 1.2117) = 1.2117 - 0.8333 x 0.35 | **0.92** (0.9200) |

I checked these numbers with the repo's own `climate_adjusted_kc`, `drip_kc_ini` and `kc_for_day` in `services/planner-service/irrigation.py`, and they match.

## Caveats

1. **The fw scaling on Kc ini is a choice, not a fixed rule.** In FAO-56, Eq. 60 scales a Kc ini that was read from Fig. 29/30. That figure depends on how often the soil is wetted, the ET0 and the soil texture. Here I scaled the Table 12 value (0.60) instead, the same way the repo's `drip_kc_ini` helper does.
   - If you don't apply fw at all, day 20 becomes **0.60** and day 50 becomes **0.91** (0.6 + 0.5 x 0.6117). Day 140 does not change.
   - If you derive Kc ini from Fig. 29/30, you need the wetting interval and the initial-period ET0. Tell me those and I can work it out.
   - Only Kc ini is scaled. Kc mid and Kc end are not scaled by fw.
2. **The planner does not apply these adjustments yet.** `build_plan` in `services/planner-service/plan.py` passes the raw `crops.py` values (0.6, 1.15, 0.80) straight to `kc_for_day`. `climate_adjusted_kc` and `drip_kc_ini` exist in `irrigation.py` but nothing in the plan path calls them. So today the planner would output 0.60, 0.875 and 0.858 for days 20, 50 and 140, not the values above.
3. **Climate inputs are per stage.** Eq. 62 should use the mid-season averages of u2 and RHmin, and Eq. 65 the averages at the end of the late season. You gave the same values for both stages, so the adjustment is the same (+0.0617) for both.
