# Bell pepper, drip, mid-season: one stressed day (FAO-56 single Kc)

**Short answer**
- The crop actually uses about **4.75 mm** today. That is the water-stressed ETc adj. Without stress it would use 6.83 mm.
- Depletion at the end of the day is about **34.75 mm**, out of a TAW of 65 mm.
- Tomorrow morning, put on about **34.75 mm net**, which refills the root zone to field capacity.

The root zone already started the day past the readily available water (30 mm > RAW 14.75 mm), so the crop was under stress all day.

## Inputs

| Input | Value |
|---|---|
| Crop | bell (sweet) pepper, mid-season |
| Kc | 1.05 (Table 12 Kc mid, as you gave it; no climate adjustment applied) |
| p (Table 22) | 0.30 |
| Soil (loam) | thetaFC 0.25, thetaWP 0.12 m3/m3 (measured values, inside the Table 19 loam ranges) |
| Zr | 0.5 m (the small end of the Table 22 range 0.5-1.0 m) |
| Dr,i-1 | 30 mm (start of today) |
| ET0 | 6.5 mm/d |
| P, I | 0 |
| RO, CR | 0 (CR = 0 assumes the water table is more than about 1 m below the root zone) |

## Steps

**1. Unstressed crop ET (Eq. 56/58)**
ETc = Kc x ET0 = 1.05 x 6.5 = **6.825 mm/d**

**2. Total available water (Eq. 82)**
TAW = 1000 x (0.25 - 0.12) x 0.5 = 1000 x 0.13 x 0.5 = **65.0 mm**

**3. Adjust p for today's ETc (Ch. 8, the note to Table 22)**
p = p(Table 22) + 0.04 x (5 - ETc) = 0.30 + 0.04 x (5 - 6.825) = 0.30 - 0.073 = **0.227**

This is inside the 0.1-0.8 limits, so no clamping is needed. On a high-demand day like this one, p comes out smaller than the table value: stress starts sooner.

**4. Readily available water (Eq. 83)**
RAW = p x TAW = 0.227 x 65.0 = **14.755 mm**

**5. Water stress coefficient (Eq. 84)**
Dr,i-1 = 30 mm, which is more than RAW (14.755 mm), so the crop is stressed:

Ks = (TAW - Dr) / ((1 - p) x TAW) = (65 - 30) / (0.773 x 65) = 35 / 50.245 = **0.6966**

**6. Actual crop water use (Eq. 81, single Kc)**
ETc adj = Ks x Kc x ET0 = 0.6966 x 6.825 = **4.754 mm**

**7. End-of-day depletion (Eq. 85, limited by Eq. 86)**
Dr,i = Dr,i-1 - (P - RO) - I - CR + ETc adj + DP = 30 - 0 - 0 - 0 + 4.754 + 0 = **34.754 mm**

- This is within 0 <= Dr <= TAW = 65 (Eq. 86).
- DP = 0 (Eq. 88): no water was added, so 0 + 0 - ETc - 30 < 0.

**8. Irrigation for tomorrow morning**
In the Annex 8 procedure, irrigation goes on the next morning when depletion is above RAW. 34.75 mm > 14.755 mm, so irrigate. The net depth refills to field capacity, so it equals the depletion: **I_net = 34.75 mm**, as a field-average depth.

## Assumptions and choices

1. **Which depletion feeds Ks.**
   - I used the start-of-day depletion (30 mm), as in Ch. 8 Example 37. AgroPilot's `daily_soil_step` does the same.
   - Annex 8 instead uses depletion after any irrigation or rain earlier that morning.
   - Today had neither, so both conventions give the same Ks here.
2. **Which ETc sets p.** I adjusted p with the unstressed ETc (Kc x ET0 = 6.825), as `daily_soil_step` does. The source writes "ETc" without saying stressed or unstressed.
   - If you skip the p adjustment and keep p = 0.30, the numbers change: RAW = 19.5 mm, Ks = 35 / (0.7 x 65) = 0.769, ETc adj = 5.25 mm, end depletion 35.25 mm, irrigation 35.25 mm.
3. **Drip.** FAO-56 scales only Kc ini by the wetted fraction fw (Eq. 60), so the mid-season Kc of 1.05 and Zr stay as they are.
   - 34.75 mm is the field-average net depth, which is the number that enters Eq. 85.
   - A depth expressed over the wetted area alone would be 34.75 / fw (fw 0.3-0.4 for trickle, Table 20). That is a separate, area-based figure.
   - Gross application, which accounts for emitter efficiency, is outside the FAO-56 note.
4. **Rounding.** I kept full precision until the end. The code gives the same values: ETc adj 4.7542 mm, Dr 34.7542 mm, Ks 0.69659, RAW 14.755 mm.
5. **What AgroPilot's plan view would do.** The planner's own plan rule (`bucket_day`) is a product choice, not FAO-56:
   - It uses no Ks, so it would count the full 6.825 mm of use.
   - It triggers only when depletion goes past 50% of TAW (32.5 mm).
   - It refills to TAW.
   - The numbers above follow the FAO-56 source.

**Practical note.** Under this p, the crop was already stressed at the start of the day, so Ks was about 0.70. To avoid this, irrigate before depletion goes past RAW (about 15 mm on days like this). With no rain and no irrigation, that comes about every 2 days at this ET.
