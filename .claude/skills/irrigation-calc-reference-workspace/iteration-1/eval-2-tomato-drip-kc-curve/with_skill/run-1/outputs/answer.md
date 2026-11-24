# Tomato on drip: Kc on season days 20, 50 and 140 (FAO-56 single Kc)

**Result**

| Season day | Stage | Kc |
|---|---|---|
| 20 | Initial (days 1-30) | **0.21** |
| 50 | Development (days 31-70) | **0.71** (0.7109) |
| 140 | Late season (days 116-145) | **0.92** (0.9200) |

## Inputs and where each comes from

- **Stage lengths, Table 11, tomato, Apr/May, Mediterranean:** 30 / 40 / 45 / 30 days (initial / development / mid / late), 145 days in total. The stages end on days 30, 70, 115 and 145.
- **Kc ini = 0.6, Table 12.** This is the Solanum group value, because the tomato cell itself is blank.
- **Kc mid(Tab) = 1.15, Table 12.** It is the unstaked value. If the plants are staked to 1.5-2 m, footnote 2 gives 1.20 instead.
- **Kc end(Tab) = 0.80.** Table 12 gives a range of 0.70-0.90 with no rule for picking a value. 0.80 is your choice, and it matches the planner preset in `crops.py`.
- **fw = 0.35.** This falls within the Table 20 trickle range of 0.3-0.4.
- **Climate, h = 0.6 m:** u2 = 3 m/s and RHmin = 30% in both the mid and late seasons. These are inside the valid ranges 1 <= u2 <= 6, 20 <= RHmin <= 80 and 0.1 < h < 10. Table 12 lists h = 0.6 m as the tomato maximum height.

## Step 1: Drip-adjusted Kc ini (Eq. 60)

Kc ini = fw x Kc ini(Table 12) = 0.35 x 0.6 = **0.21**

FAO-56 applies fw to Kc ini only (Eq. 60, with Table 20 for the fw values). Kc mid and Kc end get no fw scaling.

## Step 2: Climate-adjusted Kc mid (Eq. 62)

Kc mid = Kc mid(Tab) + [0.04 (u2 - 2) - 0.004 (RHmin - 45)] (h/3)^0.3

- Bracket: 0.04 (3 - 2) - 0.004 (30 - 45) = 0.04 + 0.06 = 0.10
- Height factor: (0.6/3)^0.3 = 0.2^0.3 = 0.61703
- Adjustment: 0.10 x 0.61703 = 0.061703

Kc mid = 1.15 + 0.061703 = **1.2117**

## Step 3: Climate-adjusted Kc end (Eq. 65)

Eq. 65 applies because Kc end(Tab) = 0.80 >= 0.45. It uses late-season means. These are the same as the mid-season values here, so the adjustment is also +0.061703.

Kc end = 0.80 + 0.061703 = **0.8617**

## Step 4: Kc curve (Eq. 66)

Kc_i = Kc_prev + [(i - SUM(L_prev)) / L_stage] x (Kc_next - Kc_prev)

Here i is the day of the season, from 1 to 145.

- **Day 20, initial stage (days 1-30):** Kc stays flat at Kc ini, so **Kc = 0.21**.
- **Day 50, development stage (days 31-70):** SUM(L_prev) = 30 and L_dev = 40.
  Kc = 0.21 + [(50 - 30)/40] x (1.2117 - 0.21) = 0.21 + 0.5 x 1.0017 = **0.7109**
- **Day 140, late season (days 116-145):** SUM(L_prev) = 30 + 40 + 45 = 115 and L_late = 30.
  Kc = 1.2117 + [(140 - 115)/30] x (0.8617 - 1.2117) = 1.2117 - 0.8333 x 0.35 = **0.9200**

The late-season drop is exactly Kc mid(Tab) - Kc end(Tab) = 0.35. This is because both stages got the same climate adjustment.

## Things to be aware of

1. **The current planner code does not produce these numbers.** `plan.py` calls
   `kc_for_day(season_day, stages, crop.kc_ini, crop.kc_mid, crop.kc_end)` with the raw presets (0.6 / 1.15 / 0.80). It does not call `drip_kc_ini` or `climate_adjusted_kc`, even though both exist in `irrigation.py`. As the code stands, it would give 0.60 on day 20, 0.875 on day 50 and 0.858 on day 140. To use the values above, it should pass
   `drip_kc_ini(0.6, 0.35)`, `climate_adjusted_kc(1.15, 3, 30, 0.6)` and `climate_adjusted_kc(0.80, 3, 30, 0.6, end=True)` into `kc_for_day`. Whether and how the planner gets u2, RHmin and h is a product decision.
2. **The development ramp starts from the drip-reduced Kc ini (0.21).** Eq. 66 uses Kc_prev = Kc ini, and Eq. 60 is what defines Kc ini under partial wetting. So the ramp starts at 0.21 rather than 0.6. That reading is my inference. The source has no separate rule for the development stage under drip.
3. **Day numbering.** Eq. 66 defines i over [1 .. season length]. The source does not say whether day 1 is the planting day. `kc_for_day` treats day 30 as the last initial day, and the numbers above follow that convention.
4. **Open choices:** I used Kc end 0.80 (from the 0.70-0.90 range) and unstaked Kc mid 1.15. A staked crop would use Kc mid 1.20, giving an adjusted Kc mid of 1.2617. That would change the values to day 50 = 0.7359 and day 140 = 0.9284.
