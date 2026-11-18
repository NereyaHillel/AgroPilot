# Bell pepper, mid-season stress day (FAO-56 single Kc)

## Results
| Quantity | Value |
|---|---|
| TAW | 72.0 mm |
| ETc unstressed | 6.30 mm/d |
| p (adjusted) | 0.248 |
| RAW | 17.86 mm |
| Ks | 0.776 |
| Stressed ETc (ETc adj) | 4.89 mm/d |
| End-of-day depletion Dr | 34.89 mm |
| Irrigate tomorrow morning? | Yes, net 34.89 mm (refill to field capacity) |

## Formulas
- TAW (Eq. 82) = 1000 (0.22 - 0.10) x 0.6 = 72 mm
- ETc = Kc x ET0 = 1.05 x 6.0 = 6.30 mm/d
- p (Table 22 + Eq. 83 adjustment) = 0.30 + 0.04 (5 - 6.30) = 0.248 (within 0.1-0.8)
- RAW = p x TAW = 0.248 x 72 = 17.856 mm
- Dr start = 30 > RAW, so Ks (Eq. 84) = (72 - 30) / ((1 - 0.248) x 72) = 42 / 54.144 = 0.7757
- Stressed ETc (Eq. 81) = 0.7757 x 6.30 = 4.887 mm/d
- Dr end (Eq. 85-86) = 30 - 0 - 0 - 0 + 4.887 = 34.887 mm (within 0 to TAW)
- Dr end 34.89 > RAW 17.86, so trigger irrigation; net depth = 34.89 mm. No deep percolation since there is no water input.

## Assumptions
- Kc mid = 1.05 (Table 12, bell pepper), no climate adjustment (Eq. 62), since u2 and RHmin were not given.
- p = 0.30 (Table 22) adjusted for ETc; the adjustment uses unstressed ETc (as in hand-checked case 3).
- Ks uses start-of-day depletion (as in case 3).
- Depletion update uses stressed ETc; no capillary rise.
- Rooting depth 0.6 m is fixed for the day (within the 0.5-1.0 m range for pepper).
- Refill rule: irrigate to field capacity when Dr > RAW, so net = end-of-day Dr. No rounding beyond two decimals; no irrigation efficiency applied (net, not gross).
