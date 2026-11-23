---
name: irrigation-calc-reference
description: Use when writing, changing, testing or reviewing irrigation planner calculations in services/planner-service - ETc, crop coefficient (Kc) curves, soil water depletion, readily available water, stress coefficient Ks, irrigation trigger or amount, tomato or bell pepper parameters, FAO-56.
---

# Irrigation calc reference (FAO-56, single Kc)

Formulas, units, planner rules and hand-checked cases for the daily planner. Equation numbers refer to FAO-56; full citations, tables and caveats live in `services/planner-service/docs/research/fao56.md`. Read it for any value not listed here. Do not recall FAO formulas from memory.

## Units
Depths in **mm**; ET0/ETc in **mm/day**; Zr in **m**; theta in **m3/m3**; u2 in **m/s**; RHmin in **%**; h in **m**; Kc, Ks, p, fw dimensionless.

## Formulas
| Quantity | Formula |
|---|---|
| ETc (Eq. 56/58) | Kc x ET0 |
| Kc on day i (Eq. 66) | Kc_prev + (i - sum(L_prev)) / L_stage x (Kc_next - Kc_prev); flat in initial and mid stages, linear in development and late |
| Kc mid / Kc end adjust (Eq. 62/65) | Kc(Tab) + [0.04(u2 - 2) - 0.004(RHmin - 45)] x (h/3)^0.3; Kc end only if Kc end(Tab) >= 0.45 |
| Kc ini, drip (Eq. 60) | fw x Kc ini; Table 20: trickle fw 0.3-0.4 |
| TAW (Eq. 82) | 1000 (thetaFC - thetaWP) Zr |
| RAW (Eq. 83) | p x TAW; p = p(Table 22) + 0.04 (5 - ETc), clamped 0.1-0.8 |
| Ks (Eq. 84) | 1 if Dr <= RAW; else (TAW - Dr) / ((1 - p) TAW) |
| Stressed ETc (Eq. 81) | Ks x Kc x ET0 |
| Depletion (Eq. 85-86) | Dr = Dr_prev - (P - RO) - I - CR + ETc adj (stressed ETc, as in case 3); then 0 <= Dr <= TAW |
| Deep percolation (Eq. 88) | DP = (P - RO) + I - ETc adj - Dr_prev, only if > 0 (stressed ETc is a choice; matters only when Ks < 1) |

## Tomato / bell pepper (Tables 11, 12, 22)
| | Kc ini | Kc mid | Kc end | h (m) | Zr max (m) | p |
|---|---|---|---|---|---|---|
| Tomato | 0.6 (group row; per-crop cell is blank) | 1.15 | 0.70-0.90 | 0.6 | 0.7-1.5 | 0.40 |
| Bell pepper | 0.6 (same) | 1.05 | 0.90 | 0.7 | 0.5-1.0 | 0.30 |

Stage lengths (init/dev/mid/late days) vary by region and planting date (Table 11); pepper init is printed "25/30".

## Hand-checked cases
1. **Kc curve.** Tomato, Mediterranean 30/40/45/30, Kc ini 0.6, mid 1.15, day 50 (development), ET0 5.0. Kc = 0.6 + (50-30)/40 x 0.55 = **0.875**; ETc = **4.375 mm/d**.
2. **Climate adjustment.** Tomato Kc mid 1.15, u2 3, RHmin 35, h 0.6. Term = (0.04 + 0.04) x (0.2)^0.3 = 0.0494; Kc mid = **1.199**; ETc at ET0 5.0 = **5.997 mm/d**.
3. **Stress day.** Pepper, loam thetaFC 0.25 / thetaWP 0.12, Zr 0.5, mid-season, ET0 5.0, no rain, no irrigation, Dr_prev 25. TAW = **65**; ETc unstressed 5.25, p = 0.29, RAW = **18.85**. Dr > RAW so Ks = 40/46.15 = **0.867**; ETc adj = **4.55**; Dr = **29.55** > RAW, so irrigate next morning, net 29.55 mm (refill to field capacity).

New code must reproduce these numbers; add them as tests.

## Planner-service plan rules
The plan in `services/planner-service` follows these rules, decided with the user (they override the FAO-56 Table 22 values above for the plan). Registry gives soil `available_water_mm_per_m`, so TAW comes from it, not from theta.

| Item | Rule |
|---|---|
| Bucket size | TAW = available_water_mm_per_m x Zr; Zr fixed: tomato 0.7 m, bell pepper 0.5 m |
| Trigger | irrigate when the level would fall below 0.5 x TAW (task spec), for both crops; no Ks and no p adjustment in the plan |
| Start | the farmer's answer for the soil the day before, required, no default: dry L = 0, half L = 0.5 x TAW, wet L = TAW |
| Day step | L_pre = max(0, min(TAW, L_prev + rain - ETc)); if L_pre < 0.5 TAW, or a refill is in progress and L_pre < TAW, then missing = TAW - L_pre and need = min(missing, daily cap); end level = L_pre + need; else need = 0 and end level = L_pre |
| Daily cap | a day runs at most 24 h: cap mm = 24 x rate mm/h. A refill that does not fit is split over days: it stays in progress (even above the trigger) until the bucket is full; rain that fills the bucket ends it |
| Past the season | Kc holds Kc end (tomato 0.80, bell pepper 0.90); the plot is not rejected |
| Litres | need_mm x area_m2 (1 mm over 1 m2 = 1 L) |
| Run time | rate mm/h = flow_lph / (row_spacing_m x emitter_spacing_m); minutes = need_mm / rate x 60 |
| Season day | (date - planting_date) in days + 1; after the last stage day, hold Kc end |
| Crop table | tomato 30/40/45/30 d, Kc 0.6 / 1.15 / 0.80; bell pepper 30/35/40/20 d, Kc 0.6 / 1.05 / 0.90 |
| Not applied | Eq. 62/65 climate adjustment (no wind or humidity in the forecast), fw scaling of Kc ini, ignoring small rain, runoff |
| Rounding | none in the engine; API response: Kc 3 decimals, mm / litres / minutes 2 decimals |

Case 4 (plan, two days). Tomato, sand 83 mm/m, area 1500 m2, row 1.5 m, emitter 0.4 m, 0.6 L/h, season day 100 (Kc 1.15), ET0 5.0 both days, no rain, level entering day 1 = 33 mm (given for this check; a real plan starts at the farmer's soil state). TAW = **58.1**, trigger 29.05, rate = **1.0 mm/h**. Day 1: ETc 5.75, L_pre 27.25 < 29.05, so need = **30.85 mm**, litres **46,275**, minutes **1,851**, end level 58.1. Day 2: L_pre = 52.35 >= 29.05, so need 0, minutes 0, end level **52.35**.
Case 5 (rain). Same plot, level 40, rain 12, ET0 5.0: L_pre = 40 + 12 - 5.75 = **46.25**, no irrigation.
Case 6 (dry start). Same plot as case 4, farmer chose dry, so level entering day 1 = 0: L_pre = max(0, 0 - 5.75) = 0 < 29.05, so 58.1 mm is missing (TAW, not TAW + ETc). The cap is 24 h x 1.0 mm/h = 24 mm, so day 1 applies **24 mm** (36,000 L, 1,440 min), end level 24. Half start (29.05): L_pre = 23.3, 34.8 mm missing, day 1 applies **24 mm**.
Case 7 (refill split over days). Case 6 plot, dry, ETc 5.75 each day, no rain. Day 1: 0 -> apply 24 -> 24. Day 2: L_pre 18.25, refill in progress, apply 24 -> **42.25**. Day 3: L_pre 36.5 (above the trigger, still refilling), missing 21.6 <= 24, apply **21.6** (1,296 min) -> 58.1, refill ends. Day 4: L_pre 52.35, need 0. West block (dry, Kc end 0.80, ET0 5.0, ETc 4.0): 24 h, 24 h, 18 h 6 min (18.1 mm).

## Still open (ask, do not invent)
Shorter plans when a stale forecast has fewer days. Annex 8 is the dual Kc (Kcb + Ke) with unverified formula mapping, so it is a structure guide only.
