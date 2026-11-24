# Bell pepper Kc on season days 30, 100 and 120 (drip, Europe/Mediterranean Apr-Jun)

## Short answer

Use initial stage = 30 days (the 125-day reading of Table 11). That is what the planner already uses in `services/planner-service/crops.py`. With it:

| Season day | Stage | Kc |
|---|---|---|
| 30 | initial (last day) | **0.60** |
| 100 | mid-season | **1.05** |
| 120 | late season (day 15 of 20) | **0.94** (0.9375) |

The answer depends on how you read the initial stage in Table 11. The table prints it as "25/30", so check that first.

## Inputs

**FAO-56 Table 11, sweet (bell) pepper, Europe and Mediterranean, Apr/Jun:**
L_ini 25/30, L_dev 35, L_mid 40, L_late 20, total 125 d.
The total of 125 d only adds up if L_ini = 30 (30+35+40+20 = 125). With L_ini = 25 the season is 120 d.

**FAO-56 Table 12, sweet pepper:** Kc ini 0.60, Kc mid 1.05, Kc end 0.90, h = 0.7 m.

**Climate adjustment (Eq. 62 for Kc mid, Eq. 65 for Kc end):**
adjustment = [0.04(u2 - 2) - 0.004(RHmin - 45)] (h/3)^0.3 = [0.04(0) - 0.004(0)] (0.233)^0.3 = **0**.
u2 = 2 m/s and RHmin = 45% are the standard climate that Table 12 assumes, so Kc mid stays 1.05 and Kc end stays 0.90.

## Kc curve (Eq. 66, day counted from 1)

Kc is flat in the initial and mid stages and changes linearly in the development and late stages:
Kc_i = Kc_prev + [(i - ΣL_prev) / L_stage] (Kc_next - Kc_prev)

### Reading A: L_ini = 30 (125 d, recommended)
Stage days: initial 1-30, development 31-65, mid 66-105, late 106-125.

- **Day 30:** the last initial day, so Kc = **0.60**. Day 31 already rises to 0.6 + (1/35)(0.45) = 0.613.
- **Day 100:** inside mid-season (66-105), so Kc = **1.05**.
- **Day 120:** late stage. Kc = 1.05 + [(120 - 105)/20](0.90 - 1.05) = 1.05 - 0.1125 = **0.9375 (about 0.94)**.

### Reading B: L_ini = 25 (120 d)
Stage days: initial 1-25, development 26-60, mid 61-100, late 101-120.

- **Day 30:** development day 5. Kc = 0.60 + (5/35)(0.45) = **0.664 (about 0.66)**.
- **Day 100:** the last mid-season day, so Kc = **1.05**.
- **Day 120:** the last day of the season, so Kc = Kc end = **0.90**.

### Comparison

| Day | Reading A (ini 30, 125 d) | Reading B (ini 25, 120 d) |
|---|---|---|
| 30 | 0.60 | 0.66 |
| 100 | 1.05 | 1.05 |
| 120 | 0.94 | 0.90 |

Only day 100 gives the same value under both readings. Days 30 and 120 both sit near a stage boundary, so the 5-day choice moves Kc by about 0.04 to 0.06, roughly 5-10% of ETc on those days.

## What the drip wetted fraction (fw = 0.4) changes

- **Not Kc mid or Kc end.** With the single-Kc method, the Table 12 mid and end values do not depend on fw, so 1.05 and 0.90 stand.
- **Kc ini, if you want to refine it.** Table 12's 0.60 is a typical value. FAO-56 Ch. 6 lets you calculate Kc ini from the wetting interval and depth (Figs. 29-30). Under partial wetting you then scale it: Kc ini = fw × Kc ini(Fig), with the figure read at depth I/fw (Eq. 60). Under drip this usually gives a lower initial Kc than 0.60. The question asks for Table 12 values, so 0.60 is kept. Treat it as an upper-end estimate for the initial stage under drip.
- **Water balance, not Kc.** fw also enters the soil-water bookkeeping and gross irrigation depth (wetted volume and application efficiency). That does not affect the Kc values here.

## Assumptions

- Day 1 is the first season day (planting or transplant), and the day number is used directly as i in Eq. 66. FAO-56 does not fix whether to count from day 0 or day 1. With day-0 counting, every value above moves by one day.
- Standard climate, so there is no climate adjustment.
- Single-Kc approach, as asked. The dual Kcb + Ke approach would handle drip partial wetting more precisely.
