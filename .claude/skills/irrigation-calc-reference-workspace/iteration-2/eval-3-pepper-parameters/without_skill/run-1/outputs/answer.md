# Bell pepper, clay loam (200 mm/m): planner parameters

Answered from general FAO-56 knowledge (Tables 12, 22), not from the planner-service code. I could not verify what the planner actually hard-codes, so check these against the code.

| Parameter | Value (FAO-56) |
|---|---|
| Kc ini | 0.60 |
| Kc mid | 1.05 |
| Kc end | 0.90 |
| Stage lengths (ini / dev / mid / late) | 25 / 35 / 40 / 20 days (120 days total) |
| Root depth Zr | 0.5 to 1.0 m (FAO-56 range); 0.7 m is a typical mid value |
| Depletion fraction p (trigger) | 0.30 |

## Bucket and trigger
TAW = 1000 x (theta_FC - theta_WP) x Zr = 200 mm/m x Zr.
RAW = p x TAW; irrigation is triggered when depletion Dr >= RAW (p = 0.30, i.e. 30 % of TAW).

| Zr | TAW | RAW (trigger depth) |
|---|---|---|
| 0.5 m | 100 mm | 30 mm |
| 0.7 m | 140 mm | 42 mm |
| 1.0 m | 200 mm | 60 mm |

Assumption: if the planner uses a single fixed root depth, the TAW is 200 mm/m x that depth. With Zr = 1.0 m it is 200 mm and the trigger is 60 mm depletion. Note FAO-56 p is for ETc around 5 mm/day and is normally adjusted by 0.04 x (5 - ETc); the planner may or may not apply that.
