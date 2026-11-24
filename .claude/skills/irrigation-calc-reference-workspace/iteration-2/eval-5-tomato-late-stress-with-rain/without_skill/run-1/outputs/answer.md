# Tomato, late season: water use, depletion, irrigation

**Answer**
- Actual crop water use today (ETc,adj): **about 5.3 mm/day**. The crop is water-stressed, so it uses less than the 6.75 mm it would use with enough water.
- End-of-day root-zone depletion (Dr): **about 52.3 mm**
- Tomorrow's net irrigation (refill to field capacity): **about 52.3 mm**

This uses the FAO-56 daily soil water balance (single Kc, with the Ks water-stress coefficient).

---

## Step 1: Potential crop ET (no stress)

ETc = Kc × ET0 = 0.90 × 7.5 = **6.75 mm/day**

## Step 2: Total available water (TAW)

TAW = 1000 × (θFC − θWP) × Zr = 1000 × (0.30 − 0.15) × 0.7 = **105 mm**

## Step 3: Depletion fraction p and readily available water (RAW)

The FAO-56 Table 22 p value for tomato is 0.40. It is meant for ETc ≈ 5 mm/day. FAO-56 says to adjust it for other ETc rates:

p = 0.40 + 0.04 × (5 − ETc) = 0.40 + 0.04 × (5 − 6.75) = 0.40 − 0.07 = **0.33**

(The result stays inside the allowed range of 0.1 to 0.8.)

RAW = p × TAW = 0.33 × 105 = **34.65 mm**

## Step 4: Is the crop stressed? (Ks)

FAO-56 computes Ks from the depletion at the **start** of the day, Dr,i−1 = 50 mm.

50 mm > RAW (34.65 mm), so the crop is stressed:

Ks = (TAW − Dr,i−1) / (TAW − RAW) = (105 − 50) / (105 − 34.65) = 55 / 70.35 = **0.782**

## Step 5: Actual crop water use

ETc,adj = Ks × ETc = 0.782 × 6.75 = **5.28 mm/day**

## Step 6: End-of-day depletion

Dr,i = Dr,i−1 − (P − RO) − I − CR + ETc,adj + DP

- P = 3 mm and RO = 0, so 3 mm of rain counts
- I = 0 (no irrigation today), CR = 0 (no capillary rise)
- DP = 0. The 3 mm of rain is far less than the 50 mm deficit, so nothing drains below the roots.

Dr,i = 50 − 3 − 0 − 0 + 5.28 + 0 = **52.28 mm ≈ 52.3 mm**

Check: 0 ≤ 52.3 ≤ TAW (105). Depletion is still above RAW, so the crop stays stressed.

## Step 7: Tomorrow's net irrigation

To bring the root zone back to field capacity, the net irrigation equals the current depletion:

In = Dr = **≈ 52.3 mm** (net, at the root zone)

Notes:
- This is a **net** amount. The gross amount is In ÷ application efficiency. For example, with drip at about 90% efficiency, that is 52.3 / 0.9 ≈ 58 mm.
- Irrigating up to field capacity tomorrow morning does not cover tomorrow's own ET. That water use starts building the depletion again. If you irrigate late in the day, add roughly tomorrow's ETc on top.
- 52 mm at once is a large application. You may want to split it into a few sets so it does not run off or drain below the roots.
- Agronomically, the crop has been below the RAW threshold since the start of today (50 > 34.65 mm). It should have been irrigated sooner. Refilling promptly limits further yield and quality loss.

## Sensitivity: if p is not adjusted

If you use the table value p = 0.40 without adjusting it: RAW = 42 mm, Ks = 55/63 = 0.873, ETc,adj = 5.89 mm, end-of-day Dr = 52.9 mm, and net irrigation is about 52.9 mm. The p adjustment matters here because ET0 is high (7.5 mm). The adjusted values above are the ones I recommend.
