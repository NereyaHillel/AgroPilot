# Bell pepper, mid-season, stress day (FAO-56 single Kc)

## Assumptions
- Kc_mid = 1.05 (FAO-56 Table 12, sweet pepper, fresh market; no local humidity/wind adjustment).
- Depletion fraction p = 0.30 (FAO-56 Table 22, pepper), adjusted for ETc per FAO-56 Annex 8: p = 0.30 + 0.04(5 - ETc), with ETc ~ 1.05*6.0 = 6.3 mm/d -> p = 0.248.
- Ks uses depletion at the START of the day (Dr,i-1 = 30 mm). No rain, irrigation, runoff, or capillary rise.
- Net irrigation = refill to field capacity.

## Results
| Quantity | Formula | Value |
|---|---|---|
| TAW | 1000 (0.22-0.10) 0.6 | 72.0 mm |
| p (adjusted) | 0.30 + 0.04(5-6.3) | 0.248 |
| RAW | p TAW | 17.9 mm |
| Ks | (TAW-Dr)/((1-p)TAW) = 42/54.14 | 0.776 |
| ETc (stressed) | Ks Kc ET0 = 0.776*1.05*6.0 | 4.89 mm |
| End-of-day Dr | 30 + 4.89 | 34.9 mm |

Dr (30) > RAW (17.9), so the crop is already stressed.

## Irrigate tomorrow morning?
Yes. End-of-day depletion 34.9 mm exceeds RAW (17.9 mm). Apply about 34.9 mm net (~35 mm) to return the root zone to field capacity (Dr = 0). Divide by application efficiency for the gross amount.

## Sensitivity (unadjusted p = 0.30)
RAW = 21.6 mm, Ks = 42/50.4 = 0.833, ETc = 5.25 mm, end Dr = 35.25 mm, irrigate ~35 mm net. Same decision.
