# Tomato, drip, day 100: Kc and ETc (FAO-56, single Kc)

## Result
- Kc on day 100 = **1.20** (Kc mid, climate-adjusted from 1.15)
- ETc = 1.20 x 5.5 = **about 6.6 mm/day** (1.1994 x 5.5 = 6.597)

## Stage lengths (FAO-56 Table 11, tomato, Mediterranean, Apr/May planting; from memory)
| Stage | Length (days) | Season days |
|---|---|---|
| Initial | 35 | 1-35 |
| Development | 45 | 36-80 |
| Mid-season | 70 | 81-150 |
| Late season | 30 | 151-180 |
| Total | 180 | |

Day 100 falls in the mid-season stage, so Kc is constant (no interpolation).

## Kc values (FAO-56 Table 12, tomato, from memory)
- Kc ini = 0.60 (not used on day 100)
- Kc mid (table) = 1.15
- Kc end = 0.80 (not used on day 100)
- Maximum crop height h = 0.6 m (Table 12)

## Climate adjustment of Kc mid (FAO-56 eq. 62)
Applied because the table value is for RHmin about 45% and u2 about 2 m/s, and the site differs:

Kc mid = Kc mid(Tab) + [0.04 (u2 - 2) - 0.004 (RHmin - 45)] (h/3)^0.3

- 0.04 x (3 - 2) = +0.040
- -0.004 x (35 - 45) = +0.040
- (0.6/3)^0.3 = 0.617
- Adjustment = 0.080 x 0.617 = +0.049
- Kc mid = 1.15 + 0.049 = 1.199, rounded to **1.20**

## Drip irrigation and 40% wetted surface
- In the single-Kc approach, localized wetting mainly lowers soil evaporation. This matters at the initial stage, where FAO-56 reduces Kc ini for drip (Kc ini is smaller with infrequent or partial wetting).
- At mid-season the canopy is nearly full cover and transpiration dominates, so no wetted-fraction reduction is applied to Kc mid.
- I did **not** multiply ETc by 0.4. Wetted fraction (fw) is relevant to the dual-Kc evaporation term and to sizing the wetted volume or application depth per irrigated area, not to scaling crop transpiration demand.

## Assumptions
1. The tomato stage lengths (35/45/70/30) and Kc values (0.60/1.15/0.80) are recalled from FAO-56 Tables 11 and 12, not looked up. Check them against the tables.
2. "Day 100" counts from planting or transplanting, so stages start at day 1.
3. The 5.5 mm/day ET0 is the FAO-56 Penman-Monteith reference value for that day and is representative of the mid-season period.
4. The wind (3 m/s at 2 m) and minimum RH (35%) are mid-season means, so eq. 62 applies directly. u2 is already at 2 m, so no height conversion is needed.
5. The crop is non-stressed, with standard (well-managed, disease-free) conditions, so Ks = 1 and ETc is potential crop ET.
6. h = 0.6 m for the (h/3)^0.3 term.
7. The ETc result is a depth over the whole field area (mm/day). Drip application depth per wetted area would need a separate conversion using the wetted fraction.
