# Bell pepper, drip, mid-season: one stress day (FAO-56)

## Inputs
- Kc mid = 1.05, ET0 = 6.5 mm, P = 0, I = 0
- θFC = 0.25, θWP = 0.12 m3/m3, Zr = 0.5 m
- Dr at start of day (Dr,i-1) = 30 mm
- p from FAO-56 Table 22 for sweet/bell pepper = 0.30

## Step 1: Unstressed crop ET (Eq. 58)
ETc = Kc x ET0 = 1.05 x 6.5 = **6.83 mm/day**

## Step 2: Total available water (Eq. 82)
TAW = 1000 (θFC - θWP) Zr = 1000 x (0.25 - 0.12) x 0.5 = **65 mm**

## Step 3: Depletion fraction p, adjusted for ETc (Ch. 8, note to Table 22)
p = p_table + 0.04 (5 - ETc) = 0.30 + 0.04 x (5 - 6.825) = 0.30 - 0.073 = **0.227**
(inside the allowed 0.1 to 0.8 range)

## Step 4: Readily available water (Eq. 83)
RAW = p x TAW = 0.227 x 65 = **14.75 mm**

## Step 5: Water stress coefficient (Eq. 84)
Dr,i-1 = 30 mm > RAW = 14.75 mm, so the crop is under water stress today.

Ks = (TAW - Dr) / ((1 - p) TAW) = (65 - 30) / (0.773 x 65) = 35 / 50.25 = **0.697**

## Step 6: Actual crop water use (Eq. 81)
ETc,adj = Ks x ETc = 0.697 x 6.825 = **4.75 mm**

The crop actually uses about **4.75 mm** today, about 2.1 mm less than the 6.83 mm it would use with no stress.

## Step 7: End-of-day depletion (Eq. 85)
Dr,i = Dr,i-1 - (P - RO) - I - CR + ETc,adj + DP = 30 - 0 - 0 - 0 + 4.75 + 0 = **34.75 mm**

(CR = 0, no water table; DP = 0, no water added. 34.75 mm is between 0 and TAW, so no clamping.)

## Step 8: Net irrigation for tomorrow morning
Dr,i = 34.75 mm > RAW (14.75 mm), so irrigate. Refilling the root zone to field capacity takes

**In = Dr,i ≈ 34.8 mm (about 35 mm net)**

That is 53% of TAW, so the soil is well past the stress threshold. It should be watered first thing.

## Summary
| Quantity | Value |
|---|---|
| ETc (no stress) | 6.83 mm |
| TAW | 65 mm |
| p (adjusted) | 0.227 |
| RAW | 14.75 mm |
| Ks | 0.697 |
| **Actual ET (ETc,adj)** | **4.75 mm** |
| **Dr at end of day** | **34.75 mm** |
| **Net irrigation tomorrow** | **≈ 34.8 mm (refill to FC)** |

## Notes and assumptions
- **Ks uses start-of-day depletion.** This follows the standard FAO-56 daily balance (Dr,i-1 in Eq. 84). If you work out Ks from mid-day or end-of-day depletion instead, you get a slightly lower Ks and ET.
- **p adjustment.** If you skip the ETc adjustment and use p = 0.30, you get RAW = 19.5 mm, Ks = 35/45.5 = 0.769, ETc,adj = 5.25 mm, Dr,end = 35.25 mm and a net irrigation of about 35.3 mm. Either way the crop is stressed.
- **Drip.** The net depth is per unit of field area, over the whole root zone as defined. FAO-56 does not scale Kc mid for the drip wetted fraction (fw), only Kc ini. Turning this into a gross amount needs the system's application efficiency, gross = net / Ea. For example, with Ea = 0.9 you would apply about 38.6 mm.
- **Kc mid climate adjustment (Eq. 62).** Kc = 1.05 is used as given. No u2/RHmin correction is applied.
- **Refill target.** "Refill to FC" means applying the full Dr. Some drip schedules refill only part of the way, to leave room for rain.
