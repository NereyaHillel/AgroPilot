# FAO-56 root-zone water balance: tomato, 2 days

## Inputs and assumptions

| Item | Value |
|---|---|
| Crop | Tomato, full cover, Kc = 1.15 (used as given; I assume it is already climate-adjusted) |
| Soil | Sandy loam, θFC = 0.23, θWP = 0.10 |
| Root zone Zr | 0.70 m |
| Starting depletion Dr,0 | 12 mm |
| Runoff RO | 0 (as you said) |
| Capillary rise CR | 0 (deep water table assumed) |
| Irrigation I | 0 on both days, unless the trigger fires |

## Soil water capacity

- **TAW** = 1000 (θFC − θWP) Zr = 1000 × (0.23 − 0.10) × 0.70 = **91.0 mm** (FAO-56 Eq. 82)
- **p** for tomato, FAO-56 Table 22: 0.40. Adjusted for ETc (Eq. 82 note: p = p_table + 0.04 (5 − ETc)), with ETc = 4.6 mm/d: p = 0.40 + 0.04 × 0.4 = **0.416**
- **RAW** = p × TAW = 0.416 × 91 = **37.9 mm**. If you use the table p of 0.40 without the adjustment, RAW is 36.4 mm. The conclusions below hold either way.

## Crop ET

ETc = Kc × ET0 = 1.15 × 4.0 = **4.6 mm/d** on both days. Depletion stays well below RAW the whole time, so Ks = 1 and ETc,adj = ETc.

## Daily balance (FAO-56 Eq. 85 and Eq. 88)

Dr,i = Dr,i−1 − (P − RO)i − Ii − CRi + ETc,i + DPi

DPi = (P − RO)i + Ii − ETc,i − Dr,i−1 ≥ 0

Depletion has a floor of 0, meaning the root zone is at field capacity. Any water left over after refilling the root zone drains below it as deep percolation.

### Day 1

- Water available: P − RO = 25 mm
- Needed to bring the soil back to field capacity: Dr,0 + ETc = 12 + 4.6 = 16.6 mm
- **Deep percolation DP1 = 25 − 4.6 − 12 = 8.4 mm**
- Without the floor, Dr,1 = 12 − 25 + 4.6 = −8.4 mm. With the floor it is **Dr,1 = 0 mm**, so the root zone ends the day at field capacity.
- Irrigation: **none**. The soil is full.

### Day 2

- Rain: 0.6 mm of drizzle. FAO-56 says rainfall below about 0.2 × ET0 usually evaporates from the soil surface and can be ignored in the water balance. Here 0.2 × 4 = 0.8 mm, and 0.6 mm is below that, so I count **effective P = 0**.
- **Dr,2 = 0 − 0 + 4.6 = 4.6 mm**. If you count the drizzle anyway, Dr,2 = 4.0 mm.
- **DP2 = 0 mm**, because the inputs do not exceed ETc plus the starting depletion.
- Irrigation: **none**. 4.6 mm is far below RAW (about 37.9 mm), so the crop is not stressed and the trigger is not reached.

## Summary

| Day | ET0 | ETc | P (effective) | Dr start | DP | Dr end | Dr ≥ RAW (37.9)? | Irrigate? |
|---|---|---|---|---|---|---|---|---|
| 1 | 4.0 | 4.6 | 25.0 | 12.0 | **8.4** | **0.0** | No | No |
| 2 | 4.0 | 4.6 | 0 (0.6 ignored) | 0.0 | **0.0** | **4.6** | No | No |

Neither day calls for irrigation. The 25 mm of rain refilled the root zone and pushed 8.4 mm below it. By the end of day 2 the depletion is only 4.6 mm, about 12% of RAW. At roughly 4.6 mm/day with no more rain, depletion would reach RAW around day 9 or 10 (37.9 / 4.6 ≈ 8.2 more days after day 2).

## Points to confirm

1. **Drizzle handling.** I ignored the 0.6 mm using FAO-56's 0.2 × ET0 guideline. If your model counts all rain, day 2 ends at 4.0 mm instead of 4.6 mm. Nothing else changes.
2. **p adjustment.** I used p = 0.416, adjusted for ETc. With a fixed p of 0.40, RAW is 36.4 mm. The decisions are the same either way.
3. **Drip.** You did not mention the irrigation system. If this is drip, the root-zone balance above is unchanged. The wetted fraction (fw) only affects the soil-evaporation part of a dual-Kc model and how a refill depth is applied, and neither comes up here because no irrigation is needed.
