# Review of `tomorrow_irrigation` against FAO-56 (single Kc)

The structure is right: Annex 8 says to irrigate the next morning once depletion passes RAW and to refill to field capacity, so net I = Dr. Most of the steps that feed that trigger are wrong, though. In order of impact:

## 1. Kc mid is scaled by fw. FAO-56 doesn't do that (biggest error)

`kc = 1.05 * fw` gives 0.3675, so ETc comes out about one third of the real value. FAO-56 uses the wetted fraction fw on drip only for **Kc ini** (Eq. 60: Kc ini = fw x Kc ini, and the Table 12 value of 0.6 is allowed, so 0.35 x 0.6 = 0.21). **Kc mid (1.05 for pepper) and Kc end (0.90) are not multiplied by fw.** In mid-season the canopy shades the whole field, so transpiration is not limited to the wetted strip. If the team wants extra drip savings past mid-season, that is a planner choice and must be labelled as one. FAO-56 does not support it.

Related: hardcoding 1.05 only fits the mid-season stage. To be correct on every day, Kc has to follow the stage curve (Eq. 66: flat in the initial and mid stages, linear in development and late season). For the true FAO mid value, Kc mid can also be climate-adjusted with Eq. 62. This is a scope question. Either pass `kc` in from the curve, or document that the function is mid-season only.

## 2. p is fixed at 0.30. It must be adjusted for that day's ETc

`raw = 0.30 * taw` uses the Table 22 value of p directly. That value only holds at ETc of about 5 mm/day. FAO-56 (Ch. 8) says p = 0.30 + 0.04 (5 - ETc), clamped to 0.1..0.8 and recomputed each day. Then RAW = p x TAW (Eq. 83). On hot days, RAW gets smaller and stress starts sooner.

## 3. Ks is computed and never used

`ks` is computed, but nothing reads it. Under stress, FAO-56 reduces ET: **ETc adj = Ks x Kc x ET0** (Eq. 81). Depletion has to grow by ETc adj, not by the unstressed ETc. Three more problems sit in the same line:
- **Wrong depletion.** Ks is computed from `dr_end`, the end-of-day depletion. It should use the start-of-day Dr,i-1 (`dr_start`), as in Ch. 8 Example 37. That is also the only order that works: you need Ks before you can compute today's depletion.
- **Hardcoded denominator.** `0.7 * taw` is (1 - p) TAW with p frozen at 0.30. With the adjusted p, it has to be (1 - p) x TAW.
- **Missing equation.** Eq. 84 is Ks = (TAW - Dr) / ((1 - p) TAW) when Dr > RAW, else 1.

## 4. The water balance isn't clamped and has no deep percolation

FAO-56 Eq. 85 is Dr,i = Dr,i-1 - (P - RO) - I - CR + ETc adj + DP, with **0 <= Dr <= TAW** (Eq. 86).
- `dr_end` is never clamped. After heavy rain it goes negative, and nothing stops it from exceeding TAW. `max(dr_end, 0)` sits inside the `dr_end > raw` branch, where dr_end is already positive, so it never does anything.
- There is no deep percolation (Eq. 88: DP = (P - RO) + I - ETc - Dr,i-1, floored at 0). Rain beyond what refills the root zone has to leave as DP. It must not be carried as negative depletion.
- `rain` goes in as gross P. FAO-56 subtracts runoff (P - RO). Pick a runoff method or state RO = 0. Also note that Ch. 8 says rain below about 0.2 x ET0 is "usually ignored". That is guidance, so state which way you went.
- Leaving out CR (capillary rise) and today's irrigation I is acceptable only under stated assumptions: CR = 0 needs a water table more than about 1 m below the root zone, and I = 0 means no irrigation was applied today.

## 5. What it costs, with numbers

Take the pepper stressed-day case: mid-season, TAW 65 mm, Dr,i-1 30 mm, ET0 6.5 mm/d, no rain.

| Step | Teammate's code | FAO-56 |
|---|---|---|
| Kc | 1.05 x 0.35 = 0.3675 | 1.05 |
| ETc | 2.389 mm | 6.825 mm |
| p / RAW | 0.30 / 19.5 mm | 0.227 / 14.755 mm |
| Ks | computed, not applied | (65 - 30) / (0.773 x 65) = 0.6966 |
| ETc adj | (none) | 4.754 mm |
| Dr end of day | 32.39 mm | 34.754 mm |
| Tomorrow's net irrigation | **32.39 mm** | **34.75 mm** |

The errors partly cancel here. Because the field is already stressed, Ks pulls ET down, and that hides part of the fw error. On an unstressed mid-season day, the fw error passes through in full: ET is under-counted by about 65 %, so the trigger fires far too late.

## Suggested shape

```python
def tomorrow_irrigation(dr_start, et0, rain, taw, kc, p_table=0.30, ro=0.0):
    # kc comes from the stage curve (Eq. 66); on drip, scale only Kc ini by fw (Eq. 60)
    etc = kc * et0                                        # Eq. 58
    p = min(max(p_table + 0.04 * (5 - etc), 0.1), 0.8)    # Ch. 8 p adjustment
    raw = p * taw                                         # Eq. 83
    ks = 1.0 if dr_start <= raw else (taw - dr_start) / ((1 - p) * taw)  # Eq. 84, start-of-day Dr
    etc_adj = ks * etc                                    # Eq. 81
    dr_end = min(max(dr_start - (rain - ro) + etc_adj, 0.0), taw)        # Eq. 85/86 (I = 0, CR = 0)
    return dr_end if dr_end > raw else 0.0                # Annex 8: refill to field capacity, net I = Dr
```

Deep percolation is (rain - ro) - etc - dr_start floored at 0 (Eq. 88), if you need to report it. Before merging, check the result against the case above (34.754 mm).

The return value is a **net**, field-average depth in mm (1 mm over 1 m2 = 1 L). Converting it to a gross amount or to drip run time is a separate step. Also note that this function implements the FAO/Annex 8 trigger. It is not the planner's `/plan` rule (`bucket_day`), which irrigates at 0.5 x TAW with no Ks or p adjustment.
