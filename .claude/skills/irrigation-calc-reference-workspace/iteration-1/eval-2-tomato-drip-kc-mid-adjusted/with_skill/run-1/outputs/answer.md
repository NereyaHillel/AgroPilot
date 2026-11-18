# Tomato, drip, day 100: Kc and ETc (FAO-56 single Kc)

## Result
- **Kc = 1.199 (about 1.20)**
- **ETc = 1.199 x 5.5 = 6.60 mm/day**

## Stage lengths (Table 11, tomato, Apr/May, Mediterranean)
Init 30 / Dev 40 / Mid 45 / Late 30 = 145 days total.

| Stage | Days (season day) |
|---|---|
| Initial | 1-30 |
| Development | 31-70 |
| Mid-season | 71-115 |
| Late | 116-145 |

Day 100 falls in mid-season (sum of init + dev = 70 < 100 <= 115), where Kc is flat, so no Eq. 66 interpolation is needed.

## Kc values and sources
| Value | Used | Source |
|---|---|---|
| Kc mid (table) | 1.15 | Table 12, tomato (planner skill / `fao56.md` section 2.2) |
| h | 0.6 m | Table 12, tomato |
| Kc ini | 0.6 (not used on day 100; with fw 0.4 would be 0.24) | Table 12 Solanum group row (per-crop cell blank); Eq. 60, Table 20 |
| Kc end | 0.70-0.90 (not used on day 100) | Table 12 |

Climate adjustment (Eq. 62), with u2 = 3 m/s, RHmin = 35%, h = 0.6 m:

- [0.04 (3 - 2) - 0.004 (35 - 45)] = 0.04 + 0.04 = 0.08
- (h/3)^0.3 = (0.2)^0.3 = 0.617
- Adjustment = 0.08 x 0.617 = 0.0494
- Kc mid = 1.15 + 0.0494 = **1.199**

Inputs are within the Eq. 62 validity ranges (1 <= u2 <= 6, 20 <= RHmin <= 80). This matches hand-checked case 2 of the skill.

ETc (Eq. 56/58) = Kc x ET0 = 1.199 x 5.5 = **6.60 mm/day** (6.596). For comparison, unadjusted 1.15 would give 6.32 mm/day.

## Role of the 40% wetted surface (drip)
FAO-56 Eq. 60 (Kc ini = fw x Kc ini(Table)) scales only the **initial-stage** Kc for partial wetting (Table 20: trickle fw 0.3-0.4). The source read does not scale Kc mid or Kc end by fw, so fw = 0.4 does **not** reduce Kc on day 100. Scaling mid-season Kc by fw (which would give about 0.48) is not supported by FAO-56 and I did not do it.

## Assumptions
1. Table 11 variant: tomato Mediterranean, Apr/May, 30/40/45/30 (the other Apr/May row, California 35/40/50/30, was not chosen because the task says Mediterranean).
2. Day 1 of the season is the planting day, so day 100 is in the mid stage (71-115). The source does not fix this, but any reasonable convention (day 1 = 0 or 1) still puts day 100 in mid-season.
3. Kc mid (table) = 1.15, h = 0.6 m (not staked; staked tomato could use up to 1.20 and a larger h).
4. u2 and RHmin are mid-season means, as Eq. 62 requires, and the 3 m/s and 35% figures are used as given.
5. ET0 of 5.5 mm/day is FAO-PM ET0 for that day.
6. Kc mid is not scaled by fw for drip (see above). This is a planner decision, flagged for the team.
7. Single Kc, non-stressed (Ks = 1). Soil-water stress (Eq. 81, Ks x Kc x ET0) is not applied because no soil or depletion data were given; if Dr > RAW, ETc would be lower. Dual-Kc evaporation component not used.
8. Kc ini 0.6 and Kc end are not needed for day 100; Kc end (0.70-0.90) remains an open planner choice for the late stage.
