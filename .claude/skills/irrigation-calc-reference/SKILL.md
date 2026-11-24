---
name: irrigation-calc-reference
description: Use when computing, checking, explaining or coding crop water use or irrigation amounts for AgroPilot tomato or bell pepper, including ET0/ETc, Kc or the Kc curve, growth stages, climate-adjusted Kc mid/end, drip wetted fraction, TAW, RAW, p, Ks water stress, root-zone depletion, rain, deep percolation, irrigation triggers or refills, the FAO-56 Annex 8 example, or work in services/planner-service irrigation.py, crops.py, plan.py and their tests, even when FAO-56 is not named.
---

# Irrigation calculation reference (FAO-56, single Kc)

## Overview

AgroPilot's planner uses FAO Irrigation and Drainage Paper 56 (Allen et al., 1998) with the single crop coefficient on a daily step. The source of truth is the verified research note at `services/planner-service/docs/research/fao56.md`; it was checked against the FAO HTML and equation images on 2026-11-24. This file condenses that note into formulas, units and three worked cases, so you don't have to rebuild the domain each session.

Read the note when you need a value that isn't here, a footnote, or a source URL. Don't fill gaps from memory: FAO-56 has many look-alike equations and tables, and recalled numbers are where answers go wrong.

## When to use

- You're computing Kc for a given day, daily ETc, depletion, stress, deep percolation, or an irrigation amount.
- You're writing or reviewing code or tests in `services/planner-service`.
- You're explaining what FAO-56 says, as opposed to what the planner does.

The note doesn't cover these: ET0 computation (Penman-Monteith, Ch. 2-4), dual-Kc evaporation (Ke), yield response (Ky) and salinity. If a task needs one of them, say so; don't improvise values.

## Units

| Quantity | Unit | Notes |
|---|---|---|
| ET0, ETc, ETc adj | mm/day | |
| P, RO, I, DP, Dr, TAW, RAW | mm | Depths. I is the field-average net depth |
| Zr, h | m | Root depth, plant height |
| thetaFC, thetaWP | m3/m3 | Volumetric water content |
| u2 | m/s | Wind at 2 m |
| RHmin | % | |
| Kc, Ks, p, fw | dimensionless | |
| Water volume | L | 1 mm over 1 m2 = 1 L (`litres` in irrigation.py) |

The source gives no rounding rule. Keep full precision and round only for display.

## Formulas

| Quantity | Formula | Source | Code |
|---|---|---|---|
| Crop ET | ETc = Kc x ET0 | Eq. 56/58 | `etc` |
| Stressed ET (single Kc) | ETc adj = Ks x Kc x ET0 | Eq. 81 | |
| Kc on season day i | Kc_i = Kc_prev + [(i - SUM L_prev) / L_stage] (Kc_next - Kc_prev). Flat in the initial and mid stages, linear in development and late season, i in [1 .. season length] | Eq. 66 | `kc_for_day` |
| Kc mid, climate adjusted | Kc mid(Tab) + [0.04 (u2 - 2) - 0.004 (RHmin - 45)] (h/3)^0.3, using mid-season means | Eq. 62 | `climate_adjusted_kc` |
| Kc end, climate adjusted | Same form, using late-season means. Apply only if Kc end(Tab) >= 0.45 | Eq. 65 | `climate_adjusted_kc(end=True)` |
| Kc ini on drip | Kc ini = fw x Kc ini(Table 12 or Fig. 29/30). The text explicitly allows the Table 12 value | Eq. 60 | `drip_kc_ini` |
| RHmin when not given | e°(Tdew) / e°(Tmax) x 100. Without dewpoint, use Tmin in place of Tdew, minus 2 °C in arid climates | Eq. 63 / 64 | |
| Total available water | TAW = 1000 (thetaFC - thetaWP) Zr | Eq. 82 | `taw` |
| Readily available water | RAW = p x TAW | Eq. 83 | |
| p adjusted for ETc | p = p(Table 22) + 0.04 (5 - ETc), clamped to 0.1..0.8, recomputed each day | Ch. 8 text | `adjusted_p` |
| Water stress | Ks = 1 if Dr <= RAW, else (TAW - Dr) / ((1 - p) TAW) | Eq. 84 | `ks_factor` |
| End-of-day depletion | Dr,i = Dr,i-1 - (P - RO) - I - CR + ETc adj + DP, then clamped to 0 <= Dr <= TAW | Eq. 85, 86 | `daily_soil_step` |
| Deep percolation | DP = (P - RO) + I - ETc - Dr,i-1, floored at 0 | Eq. 88 | `daily_soil_step` |
| Starting depletion from measured theta | Dr = 1000 (thetaFC - theta) Zr | Eq. 87 | |

Valid ranges for Eq. 62 and Eq. 65:
- 1 <= u2 <= 6 and 20 <= RHmin <= 80.
- Plant height: Eq. 62 requires 0.1 < h < 10 (strict); Eq. 65 allows 0.1 <= h <= 10.

Conventions the source backs:
- **Which depletion feeds Ks:** use the start-of-day Dr,i-1, as Ch. 8 Example 37 (a tomato) does. Annex 8 instead uses depletion after that morning's rain or irrigation.
- **Capillary rise:** CR = 0 when the water table is more than about 1 m below the root zone.
- **Small rain:** rain below about 0.2 x ET0 is "usually ignored" (Ch. 8). That's guidance, not a hard rule, so state which way you went.

## Crop values

| | Tomato | Bell pepper |
|---|---|---|
| Kc ini (Table 12) | 0.6, the Solanum group value (the per-crop cell is blank, and Ch. 6 says the group value covers the group) | 0.6 |
| Kc mid | 1.15 (1.20 if staked to 1.5-2 m) | 1.05 (1.15 if staked) |
| Kc end | 0.70-0.90 range | 0.90 |
| h | 0.6 m | 0.7 m |
| p (Table 22, valid at ETc about 5 mm/d) | 0.40 | 0.30 |
| Zr max (Table 22) | 0.7-1.5 m | 0.5-1.0 m |
| Stage lengths (Table 11, ini/dev/mid/late, days) | Mediterranean Apr/May: 30/40/45/30. Other rows are in the note | Europe/Mediterranean Apr/Jun: "25/30"/35/40/20 (the cell prints two values) |
| Planner preset (`crops.py`) | Kc end 0.80, Zr 0.7 m | Initial stage 30 d, Zr 0.5 m |

- **Wetted fraction (Table 20):** fw is 0.3-0.4 for trickle (drip) irrigation and 1.0 for rain or sprinkler.
- **Soil water (Table 19):** this table gives thetaFC/thetaWP ranges by soil texture; they are in the note. When measured values are given, use those.

## Worked cases

These were calculated by hand and match `irrigation.py` to full precision. Use them as test oracles and as checks on your own arithmetic.

### Case 1: pepper, stressed day

Inputs: Kc 1.05 (mid-season), thetaFC 0.25, thetaWP 0.12, Zr 0.5 m, Dr,i-1 30 mm, ET0 6.5 mm/d, no rain and no irrigation.

1. ETc = 1.05 x 6.5 = **6.825** mm (Eq. 58).
2. TAW = 1000 x 0.13 x 0.5 = **65** mm (Eq. 82).
3. p = 0.30 + 0.04 x (5 - 6.825) = **0.227** (Ch. 8).
4. RAW = 0.227 x 65 = **14.755** mm (Eq. 83).
5. Dr,i-1 is 30 mm, which is above RAW, so the crop is stressed. Ks = (65 - 30) / (0.773 x 65) = **0.6966** (Eq. 84).
6. ETc adj = 0.6966 x 6.825 = **4.754** mm (Eq. 81).
7. Dr = 30 + 4.754 = **34.754** mm, and DP = 0 (Eq. 85, 88).
8. Dr is above RAW, so tomorrow morning's net irrigation is **34.75 mm**, a refill to field capacity.

If you skip the p adjustment (step 3), you get RAW 19.5, Ks 0.769 and Dr 35.25. That's the most common slip.

### Case 2: tomato on drip, Kc curve

Inputs: stages 30/40/45/30, fw 0.35, Kc end(Tab) 0.80. Mid and late season both average u2 3 m/s, RHmin 30% and h 0.6 m.

1. Kc ini = 0.35 x 0.6 = **0.21** (Eq. 60).
2. Climate term = [0.04 x 1 - 0.004 x (-15)] x (0.6/3)^0.3 = 0.10 x 0.6170 = 0.0617.
   - Kc mid = 1.15 + 0.0617 = **1.2117** (Eq. 62).
   - Kc end = 0.80 + 0.0617 = **0.8617** (Eq. 65; 0.80 is at least 0.45).
3. Day 20 is in the initial stage, so Kc = **0.21**.
4. Day 50 is in development: Kc = 0.21 + (20/40)(1.2117 - 0.21) = **0.7109**.
5. Day 140 is in the late season: Kc = 1.2117 + (25/30)(0.8617 - 1.2117) = **0.9200**.

Kc mid and Kc end are **not** multiplied by fw.

Note: `plan.py` currently passes the raw presets (0.6, 1.15, 0.80) to `kc_for_day` and never calls `drip_kc_ini` or `climate_adjusted_kc`. The plan therefore gives 0.60, 0.875 and 0.858 for these days.

### Case 3: tomato, rain and deep percolation

Inputs: Kc 1.15, thetaFC 0.23, thetaWP 0.10, Zr 0.7 m, Dr,i-1 12 mm, ET0 4 mm/d on both days. Day 1 has 25 mm of rain with RO = 0. Day 2 has 0.6 mm of rain.

1. TAW = 1000 x 0.13 x 0.7 = **91** mm.
2. ETc = 4.6 mm, p = 0.40 + 0.04 x 0.4 = 0.416, RAW = **37.856** mm.
3. Day 1: Ks = 1.
   - Dr = 12 - 25 + 4.6 = -8.4, clamped to **0** (Eq. 86).
   - DP = 25 - 4.6 - 12 = **8.4** mm (Eq. 88).
4. Day 2: the 0.6 mm is below 0.2 x 4 = 0.8, so it is usually ignored.
   - Ignoring it: Dr = **4.6** mm.
   - Counting it: Dr = 4.0 mm. `daily_soil_step` has no cutoff, so it counts the rain and gives 4.0. The `/plan` loop applies `effective_rain` and ignores it.
5. No irrigation on either day: depletion stays below RAW.

## FAO-56 vs the planner's plan rule

The FAO trigger, from Annex 8, is to irrigate the next morning when depletion exceeds RAW and refill to field capacity (net I = Dr). `irrigation_decision` implements it.

The `/plan` endpoint uses `bucket_day` instead, which is a product choice:
- It irrigates when the level would drop below 0.5 x TAW, and refills to TAW.
- It applies no Ks and no p adjustment.
- A day's application is capped at `MAX_RUN_HOURS` (24 h) of drip; a larger refill continues on the next days.
- Rain below 0.2 x ET0 is ignored (`effective_rain`); `daily_soil_step` still counts all rain.

Always say which of the two you're describing.

## Common mistakes

| Mistake | Correct |
|---|---|
| Treating fw x Table 12 Kc ini as an unsupported choice | Eq. 60's text explicitly allows the Table 12 value |
| Scaling Kc mid or Kc end, or changing Zr, for drip | FAO-56 scales only Kc ini. Anything more is a planner choice to flag |
| Leaving p at the Table 22 value | Adjust p with that day's ETc and clamp it to 0.1..0.8 |
| Computing Ks from the end-of-day depletion | Use the start-of-day depletion (Example 37) |
| Using Eq. 80 for the planner | Eq. 80 is the dual-Kc formula. The single-Kc planner uses Eq. 81 |
| Using Annex 8 as a numeric test oracle | Annex 8 is a dual-Kc dry-bean example. Use it for structure only (step order, trigger, refill, root growth by Eq. 8-1). Its numbers appear only for 15-27 May, Box 8.1 has typos, footnote 9 names column AK where AL is meant, and its Kcb end 0.23 should stay 0.25 |
| Adjusting a tabulated Kc end below 0.45 | Leave it unchanged |
| Presenting a choice as if FAO-56 fixed it | Label it as a choice. Open choices: tomato Kc end within 0.70-0.90; pepper initial stage 25 or 30 d; which Table 11 row; Zr within the Table 22 range; the day-1 convention; the small-rain cutoff; the runoff method |
