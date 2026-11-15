# 5-day plan, bell pepper plot, 2026-06-10 to 2026-06-14

## Assumptions (FAO-56, from general knowledge)
- Pepper Kc: ini 0.6, mid 1.05, end 0.90. Stages 25/35/40/20 days. Planted 2026-04-22, so 2026-06-10 is DAP 49, which is in the development stage (days 25-60).
  Kc = 0.6 + (DAP-25)/35 * 0.45.
- Root depth Zr = 0.7 m, depletion fraction p = 0.30 (pepper). TAW = 83 x 0.7 = 58.1 mm, RAW = 17.4 mm. Ks = 1 while depletion < RAW.
- Bucket starts full (depletion 0) on 2026-06-10 morning. Rain is fully effective (no runoff or interception loss).
- Trigger: irrigate when end-of-day depletion exceeds RAW, refilling to field capacity. Irrigation is applied on that day.
- Emitter application rate = 1.6 / (0.3 x 1.2) = 4.44 mm/h over the plot area. Drip efficiency 90% (gross = net / 0.9). With efficiency 1.0, litres and minutes are the net values shown in brackets.
- need_mm is net refill depth. Bucket level = available water in the root zone = TAW - depletion.

## Plan
| Date | Kc | ETc mm | Rain mm | need_mm | litres | run_minutes | Bucket end of day (mm) |
|---|---|---|---|---|---|---|---|
| 06-10 | 0.909 | 5.91 | 0 | 0 | 0 | 0 | 52.2 |
| 06-11 | 0.921 | 6.45 | 0 | 0 | 0 | 0 | 45.7 |
| 06-12 | 0.934 | 6.54 | 5 | 0 | 0 | 0 | 44.2 |
| 06-13 | 0.947 | 5.68 | 0 | 19.58 | 8702 (net 7832) | 294 (net 264) | 58.1 (full, after irrigation) |
| 06-14 | 0.960 | 5.76 | 0 | 0 | 0 | 0 | 52.3 |

Depletion before irrigation on 06-13 is 19.58 mm, above RAW 17.4 mm, which triggers the single irrigation of the period (about 4.9 h of run time).
