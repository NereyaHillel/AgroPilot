# FAO-56 root-zone water balance: tomato, 2 days

Method: FAO-56 single-Kc, Ch. 8 root-zone balance (Eqs. 81-88). Ks uses start-of-day depletion, as in Ch. 8 Example 37.

## Inputs and assumptions
- Kc = 1.15 (Table 12 tomato Kc mid, full cover; given)
- thetaFC = 0.23, thetaWP = 0.10 m3/m3 (given, inside the Table 19 sandy-loam ranges 0.18-0.28 / 0.06-0.16)
- Zr = 0.7 m (given; small end of the Table 22 range 0.7-1.5 m)
- p(Table 22, tomato) = 0.40
- Dr,0 = 12 mm (start of day 1)
- RO = 0 (given). CR = 0 (assumption: water table more than about 1 m below the root zone). I = 0 unless triggered.

## Fixed quantities
- **TAW** (Eq. 82) = 1000 x (0.23 - 0.10) x 0.7 = **91.0 mm**
- **ETc** (Eq. 56/58) = 1.15 x 4 = **4.6 mm/d** (same both days)
- **p adjusted** (Ch. 8 text) = 0.40 + 0.04 x (5 - 4.6) = **0.416** (inside 0.1-0.8)
- **RAW** (Eq. 83) = 0.416 x 91.0 = **37.86 mm**

## Day 1 (ET0 4 mm, P 25 mm, RO 0)
- Ks (Eq. 84): Dr,0 = 12 <= RAW 37.86, so **Ks = 1**. ETc adj (Eq. 81) = 1 x 1.15 x 4 = 4.6 mm.
- Rain check: 25 mm is well above 0.2 x ET0 = 0.8 mm, so it counts.
- **DP** (Eq. 88) = (P - RO) + I - ETc - Dr,i-1 = 25 - 0 + 0 - 4.6 - 12 = **8.4 mm** (>= 0, so it drains).
- **Dr,1** (Eq. 85) = 12 - 25 - 0 - 0 + 4.6 + 8.4 = **0.0 mm** (root zone at field capacity; consistent with Eq. 86, 0 <= Dr <= TAW).

Rain covered the 12 mm deficit plus the day's 4.6 mm ETc (16.6 mm in total). The remaining 8.4 mm drained below the root zone.

**Irrigation:** no. Dr = 0 is far below RAW (37.86 mm).

## Day 2 (ET0 4 mm, P 0.6 mm)
- Ks: Dr,1 = 0 <= RAW, so **Ks = 1**. ETc adj = 4.6 mm.
- Rain check: 0.6 mm < 0.2 x ET0 = 0.8 mm. Ch. 8 says rain this small is "usually ignored". That is guidance, not a hard rule (open choice), so here are both cases:

| | Drizzle ignored (Ch. 8 guidance, my primary answer) | Drizzle counted |
|---|---|---|
| DP (Eq. 88) | 0 - 4.6 - 0 < 0, so **0 mm** | 0.6 - 4.6 - 0 < 0, so **0 mm** |
| Dr,2 (Eq. 85) | 0 - 0 + 4.6 = **4.6 mm** | 0 - 0.6 + 4.6 = **4.0 mm** |

**Irrigation:** no either way. 4.0-4.6 mm is far below RAW (37.86 mm).

## Summary

| Day | Ks | ETc adj (mm) | DP (mm) | Dr end of day (mm) | Irrigate? |
|---|---|---|---|---|---|
| 1 | 1 | 4.6 | 8.4 | 0.0 | No |
| 2 | 1 | 4.6 | 0 | 4.6 (4.0 if drizzle counted) | No |

Neither day calls for irrigation. Under the FAO Annex 8 scheduling rule, you irrigate the next morning only when end-of-day Dr is greater than RAW, and then refill by I = Dr (back to field capacity). The water balance is far from that point: at about 4.6 mm/d with no more rain, Dr would first exceed 37.86 mm around day 10 (0 + 9 x 4.6 = 41.4 mm at the end of day 10). That projection assumes conditions stay the same.

## Notes on choices
- **Which Dr feeds Ks:** I used start-of-day depletion (Example 37). The Annex 8 convention uses depletion after the morning's rain. Here that also gives Ks = 1 on both days, so the result is the same either way.
- **Drizzle under 0.2 ET0:** I ignored it as the primary answer and showed the counted case. The difference is 0.6 mm.
- **AgroPilot planner vs FAO-56:** the answer above follows the FAO-56 source. The planner's own plan rule (`bucket_day` in `services/planner-service/irrigation.py`) is a product choice. It triggers when depletion goes past 50% of TAW (45.5 mm here), refills to TAW, and applies no Ks or p adjustment. That rule would not irrigate on either day either. Also, `daily_soil_step` in the same file has no 0.2 ET0 cutoff. It would count the 0.6 mm and give Dr,2 = 4.0 mm.
