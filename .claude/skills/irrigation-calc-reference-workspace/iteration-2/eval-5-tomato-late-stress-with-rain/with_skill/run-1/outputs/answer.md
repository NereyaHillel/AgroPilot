# Tomato, late season: stressed day with morning rain

FAO-56 single-Kc daily water balance (Eqs. 58, 81-88, Ch. 8 p adjustment). The FAO trigger rule used here is from Annex 8: irrigate the next morning if depletion is above RAW, and refill to field capacity.

**Inputs:** Kc 0.90, thetaFC 0.30, thetaWP 0.15, Zr 0.7 m, Dr,i-1 = 50 mm, P = 3 mm, RO = 0, ET0 = 7.5 mm/d, no irrigation today. CR = 0 (I'm assuming the water table is deep).

## Steps

1. **Unstressed crop ET (Eq. 58):** ETc = Kc x ET0 = 0.90 x 7.5 = **6.75 mm**

2. **Total available water (Eq. 82):** TAW = 1000 x (0.30 - 0.15) x 0.7 = **105 mm**

3. **Depletion fraction p, adjusted for today's ETc (Ch. 8):**
   p = p(Table 22, tomato) + 0.04 x (5 - ETc) = 0.40 + 0.04 x (5 - 6.75) = 0.40 - 0.07 = **0.33** (inside the 0.1-0.8 clamp)

4. **Readily available water (Eq. 83):** RAW = 0.33 x 105 = **34.65 mm**

5. **Water stress Ks (Eq. 84), from start-of-day depletion (as in Ch. 8 Example 37):**
   Dr,i-1 = 50 mm, which is above RAW (34.65 mm), so the crop is stressed.
   Ks = (TAW - Dr,i-1) / ((1 - p) x TAW) = (105 - 50) / (0.67 x 105) = 55 / 70.35 = **0.7818**

6. **Actual crop water use (Eq. 81):** ETc adj = Ks x Kc x ET0 = 0.7818 x 6.75 = **5.28 mm** (5.2772)

7. **Rain:** 3 mm is above 0.2 x ET0 = 1.5 mm, so it isn't in the "usually ignored" small-rain range. I count it in full, since there's no runoff: P - RO = 3 mm.

8. **Deep percolation (Eq. 88):** DP = (P - RO) + I - ETc - Dr,i-1 = 3 + 0 - 6.75 - 50 < 0, so **DP = 0**

9. **End-of-day depletion (Eq. 85):**
   Dr,i = Dr,i-1 - (P - RO) - I - CR + ETc adj + DP = 50 - 3 - 0 - 0 + 5.2772 + 0 = **52.28 mm**
   This is between 0 and TAW (105), so the clamp in Eq. 86 doesn't change it.

10. **Irrigation for tomorrow (FAO / Annex 8 trigger):** Dr = 52.28 mm is above RAW = 34.65 mm, so irrigate tomorrow morning and refill to field capacity:
    **Net irrigation = Dr = 52.28 mm** (52.3 L/m2 field-average net depth, before you account for application efficiency).

## Answer

| Quantity | Value |
|---|---|
| ETc (unstressed) | 6.75 mm |
| TAW / p / RAW | 105 mm / 0.33 / 34.65 mm |
| Ks | 0.782 |
| **Actual crop water use, ETc adj** | **5.28 mm** |
| Deep percolation | 0 mm |
| **End-of-day depletion** | **52.28 mm** |
| **Tomorrow's net irrigation** | **52.28 mm** (refill to FC) |

## Notes and choices

- **Common slip:** if you leave p at 0.40, you get RAW = 42 mm, Ks = 55/63 = 0.873, ETc adj = 5.89 mm and Dr = 52.89 mm. Adjusting p for ETc is what FAO-56 calls for.
- **Which depletion feeds Ks (a choice):** I used the start-of-day 50 mm, following Ch. 8 Example 37, a tomato. Annex 8 instead uses the depletion after that morning's rain (47 mm). With that convention Ks = 58/70.35 = 0.8244, ETc adj = 5.57 mm, Dr = 52.57 mm, and tomorrow's net irrigation is 52.57 mm.
- **Kc 0.90:** this sits at the top of FAO's tomato Kc end range (0.70-0.90). I used it as given, as today's late-season Kc. The planner preset Kc end is 0.80.
- **Planner's `/plan` rule vs FAO-56:** the numbers above follow the FAO trigger (`irrigation_decision`). The `/plan` endpoint uses `bucket_day`, which applies no Ks and no p adjustment. It irrigates when the level would drop below 0.5 x TAW = 52.5 mm. Without Ks, today's depletion would be 50 - 3 + 6.75 = 53.75 mm, leaving a level of 51.25 mm. That is below 52.5 mm, so that rule would also trigger a refill to TAW, but from a different depletion figure.
- Net irrigation is the depth delivered to the root zone. The gross application is net divided by system efficiency, and that efficiency isn't given here.
