# Tomato plot plan, 2026-07-01 to 2026-07-04

Calculated by hand from the planner rules in `irrigation-calc-reference/SKILL.md`.

## Choosing Kc from the planting date
- Season day = (date - planting date) in days + 1.
- Planting 2025-01-01 to 2026-07-01 is 365 + 181 = 546 days, so 2026-07-01 is season day **547**. The four forecast days are season days 547 to 550.
- The plan's tomato table is 30/40/45/30 days, which totals 145 days. Days 547 to 550 are far past the last stage day.
- The rule for that case is to hold Kc end, which is **0.80** for tomato. The plan does not use the stage-day logic or Kc mid here.
- The planting date is more than a year old, so this is a past-season plot. The skill lists "hold Kc end or reject a past-season plot" as an open question. I followed the current rule (hold Kc end) and did not ask, as you instructed. If the planner should reject such plots instead, none of the numbers below would apply.

## Parameters
- TAW = 200 mm/m x 0.7 m (fixed tomato Zr) = **140 mm**.
- Trigger = 0.5 x TAW = **70 mm**.
- The bucket starts full, so the level at the start of day 1 is 140 mm.
- ETc = 0.80 x 7.0 = **5.6 mm/day**.
- Emitter rate = 1.0 / (1.5 x 0.4) = **1.667 mm/h**.
- Litres = need_mm x 1000 m2.

## Daily results
| Date | Season day | Kc | Rain (mm) | ETc (mm) | L_pre (mm) | need_mm | litres | run_minutes | end-of-day level (mm) |
|---|---|---|---|---|---|---|---|---|---|
| 2026-07-01 | 547 | 0.800 | 0 | 5.6 | 134.4 | 0 | 0 | 0 | 134.4 |
| 2026-07-02 | 548 | 0.800 | 60 | 5.6 | min(140, 134.4 + 60 - 5.6 = 188.8) = 140 | 0 | 0 | 0 | 140.0 |
| 2026-07-03 | 549 | 0.800 | 0 | 5.6 | 134.4 | 0 | 0 | 0 | 134.4 |
| 2026-07-04 | 550 | 0.800 | 0 | 5.6 | 128.8 | 0 | 0 | 0 | 128.8 |

## Notes
- Day 2: the 60 mm of rain overfills the bucket. The level is capped at TAW (140 mm). The 48.8 mm of excess is lost as deep percolation, and the plan does not track it.
- The level never gets near the 70 mm trigger, so no irrigation is needed on any of the 4 days. All need, litres and run-minute values are 0.
- The result does not depend on the rain. Even with no rain at all, the level would only fall from 140 mm to 117.6 mm over 4 days.
