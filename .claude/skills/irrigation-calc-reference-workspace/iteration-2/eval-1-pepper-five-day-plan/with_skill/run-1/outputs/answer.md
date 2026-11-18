# Bell pepper 5-day plan, 2026-06-10 to 2026-06-14

Rules from the irrigation-calc-reference skill (planner-service plan rules).

## Derived parameters
- Season day on 2026-06-10 = (06-10 minus 04-22) + 1 = 49 + 1 = 50. Pepper stages 30/35/40/20 d: days 31-65 are development, so Kc is linear from 0.6 to 1.05.
- Kc(i) = 0.6 + (i - 30)/35 x 0.45
- TAW = 83 mm/m x 0.5 m (fixed Zr) = 41.5 mm. Trigger = 0.5 x TAW = 20.75 mm. Bucket starts full (41.5).
- Rate = 1.6 / (1.2 x 0.3) = 4.444 mm/h. Area 400 m2 (1 mm = 400 L).
- Day step: L_pre = min(TAW, L_prev + rain - ETc). If L_pre < 20.75, need = 41.5 - L_pre and end level = 41.5; otherwise need = 0.

## Plan
| Date | Season day | ET0 | Rain | Kc | ETc | L_pre | need_mm | litres | run_minutes | end level (mm) |
|---|---|---|---|---|---|---|---|---|---|---|
| 06-10 | 50 | 6.5 | 0 | 0.857 | 5.571 | 35.93 | 0.00 | 0.00 | 0.00 | 35.93 |
| 06-11 | 51 | 7.0 | 0 | 0.870 | 6.090 | 29.84 | 0.00 | 0.00 | 0.00 | 29.84 |
| 06-12 | 52 | 7.0 | 5 | 0.883 | 6.180 | 28.66 | 0.00 | 0.00 | 0.00 | 28.66 |
| 06-13 | 53 | 6.0 | 0 | 0.896 | 5.374 | 23.28 | 0.00 | 0.00 | 0.00 | 23.28 |
| 06-14 | 54 | 6.0 | 0 | 0.909 | 5.451 | 17.83 | 23.67 | 9466.86 | 319.51 | 41.50 |

Day 5: 17.83 < 20.75, so refill to full: need = 41.5 - 17.83 = 23.67 mm, litres 9,466.86, minutes = 23.667 / 4.444 x 60 = 319.51 (about 5.3 h, under 24 h).

## Assumptions
- Bucket full at start of 06-10 (plan rule). Rain is added to the bucket the same day, capped at TAW; no runoff, no small-rain ignoring.
- No Ks, no Eq. 62/65 climate adjustment, no fw scaling of Kc ini (plan rules).
- Forecast is fresh and has all 5 days, so no stale-forecast case.
- The bucket is the plan-rule 0.5 m x 83 mm/m, not FAO Table 22 p.
- Values unrounded in calculation; shown to the API precision (Kc 3 decimals, others 2).
