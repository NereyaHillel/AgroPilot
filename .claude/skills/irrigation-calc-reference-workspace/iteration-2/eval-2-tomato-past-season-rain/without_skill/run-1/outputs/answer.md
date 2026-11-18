# Tomato plot, forecast 2026-07-01 to 2026-07-04

## Choosing Kc given the planting date
The registry planting date is 2025-01-01. The forecast starts 2026-07-01, which is 546 days later. A FAO-56 tomato season is about 145 days (30 initial, 40 development, 45 mid, 30 late), so that season ended long ago. Reading the date literally would put the crop past late-season, which would mean Kc_end = 0.8 or no crop at all.

I treat the date as a stale record from a past season. It cannot tell us the stage of whatever is growing now. Since I cannot ask, I assumed a crop is in the ground and at peak demand, and used FAO-56 **Kc_mid = 1.15** for all four days. This is the safer choice because it avoids under-irrigating. If the date is confirmed to be current and the crop is in late season, use Kc 0.8 instead. Then ETc is 5.6 mm and every irrigating day scales by 0.8/1.15 = 0.696. The planting date should be updated in the registry.

## Assumptions
- Root depth 1.0 m, so TAW = 200 mm. Depletion fraction p = 0.4, so RAW = 80 mm. Ks = 1 throughout, because depletion stays far below RAW.
- Bucket assumed full (field capacity, 200 mm) at the start of day 1. Rain is treated as fully effective, and any overflow above 200 mm drains.
- Irrigation efficiency is taken as 100%. Each day's need is ETc minus rain, floored at 0, and is applied that day to keep the bucket full.
- Emitter density is 1 / (0.4 m x 1.5 m) = 1.667 emitters/m2. At 1.0 L/h each that is 1.667 mm/h, or 1666.7 L/h for 1000 m2.

## Results (ETc = 1.15 x 7.0 = 8.05 mm/day)

| Day | Kc | ETc mm | Rain mm | need_mm | litres | run_minutes | End-of-day bucket mm |
|---|---|---|---|---|---|---|---|
| 2026-07-01 | 1.15 | 8.05 | 0 | 8.05 | 8050 | 289.8 | 200 |
| 2026-07-02 | 1.15 | 8.05 | 60 | 0 | 0 | 0 | 200 (51.95 mm surplus drains) |
| 2026-07-03 | 1.15 | 8.05 | 0 | 8.05 | 8050 | 289.8 | 200 |
| 2026-07-04 | 1.15 | 8.05 | 0 | 8.05 | 8050 | 289.8 | 200 |

Run minutes = litres / 1666.7 L/h x 60.

If the planner instead waits until depletion reaches RAW before irrigating, nothing would be applied in these 4 days. The bucket would go 191.95, then 200 (rain refills it), then 191.95, then 183.9 mm.
