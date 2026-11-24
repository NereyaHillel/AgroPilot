# Bell pepper on drip: Kc on season days 30, 100 and 120

## Short answer

Table 11 prints the initial stage for this row as **"25/30"**: two values in one cell, and FAO-56 doesn't say which to use. Day 100 comes out the same either way. Days 30 and 120 depend on your choice:

| Season day | Initial stage 25 d (season 120 d) | Initial stage 30 d (season 125 d) |
|---|---|---|
| 30 | **0.3557** (development) | **0.24** (initial) |
| 100 | **1.05** (last day of mid-season) | **1.05** (mid-season) |
| 120 | **0.90** (last day of the season) | **0.9375** (late season) |

You need to pick one and record it. If you want a default, use **30 d**, for two reasons:
- The row's printed total is 125 days, and 30 + 35 + 40 + 20 = 125. With 25 the total would be 120. This is my inference: FAO-56 doesn't explain the cell.
- The planner preset in `crops.py` already uses `Stages(30, 35, 40, 20)`.

Either way it's a choice, not something FAO-56 fixes.

## Inputs

- **Stages (Table 11, Europe/Mediterranean, Apr/Jun):** initial 25 or 30 d, development 35 d, mid-season 40 d, late season 20 d.
- **Kc values (Table 12, sweet pepper):**
  - Kc ini 0.6. The pepper cell is blank, so this is the Solanum group value, which Ch. 6 says covers the whole group.
  - Kc mid 1.05 (not staked).
  - Kc end 0.90.
  - h 0.7 m.
- **Drip, Eq. 60:** Kc ini = fw x Kc ini(Table 12) = 0.4 x 0.6 = **0.24**. The Eq. 60 text explicitly allows the Table 12 value. fw 0.4 is the top of the Table 20 trickle range (0.3-0.4).
- **Climate adjustment, Eq. 62 for Kc mid and Eq. 65 for Kc end:** the term is [0.04 (2 - 2) - 0.004 (45 - 45)] (0.7/3)^0.3 = **0**.
  - Kc mid stays 1.05.
  - Kc end stays 0.90. Eq. 65 would apply, since 0.90 >= 0.45, but the term is zero.
  - Table 12 is already tabulated for u2 2 m/s and RHmin 45%, so this result is expected.
- **Kc mid and Kc end are not multiplied by fw.** FAO-56 scales only Kc ini for drip.

## Working (Eq. 66)

Kc_i = Kc_prev + [(i - SUM L_prev) / L_stage] (Kc_next - Kc_prev). Kc is flat in the initial and mid-season stages and linear in development and late season. i counts from 1.

### Option A: initial stage 25 d

Initial is days 1-25, development 26-60, mid-season 61-100 and late season 101-120.

- **Day 30** is in development:
  - Kc = 0.24 + (30 - 25)/35 x (1.05 - 0.24)
  - = 0.24 + 0.142857 x 0.81
  - = **0.3557**
- **Day 100** is the last day of mid-season, so Kc = **1.05**. Interpolating with the late-season formula at i = 100 gives (100 - 100)/20 = 0, which is the same value.
- **Day 120** is the last day of the season:
  - Kc = 1.05 + (120 - 100)/20 x (0.90 - 1.05)
  - = **0.90**

### Option B: initial stage 30 d

Initial is days 1-30, development 31-65, mid-season 66-105 and late season 106-125.

- **Day 30** is the last day of the initial stage, so Kc = **0.24**.
- **Day 100** is in mid-season, so Kc = **1.05**.
- **Day 120** is in the late season:
  - Kc = 1.05 + (120 - 105)/20 x (0.90 - 1.05)
  - = 1.05 - 0.75 x 0.15
  - = **0.9375**

Day 30 sits on the stage boundary in both options, so the 5-day difference moves it from flat Kc ini (0.24) to partway up the development ramp (0.356), about 48% higher. Day 120 differs by about 4%.

## What the planner currently does (not FAO-56)

`plan.py` passes the raw presets to `kc_for_day`: 30 d initial stage, Kc ini 0.6, Kc mid 1.05, Kc end 0.90. It never calls `drip_kc_ini` or `climate_adjusted_kc`. So `/plan` gives these values:

- Day 30: **0.60**. That's the un-scaled Kc ini, 2.5x the drip-corrected 0.24.
- Day 100: **1.05**.
- Day 120: **0.9375**.

In this standard climate the missing climate adjustment changes nothing. The missing fw scaling on Kc ini changes the whole initial stage, and the development ramp starts from 0.6 instead of 0.24.

## Choices to record

- **Initial stage, 25 or 30 d:** the "25/30" cell is ambiguous in the source.
- **fw = 0.4:** within the Table 20 trickle range of 0.3-0.4.
- **Kc mid 1.05:** this assumes the pepper is not staked. If it's staked to 1.5-2 m, footnote 2 allows Kc mid 1.15 with a larger h.
