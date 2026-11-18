# First irrigation in the planner bucket model

Rules used (skill irrigation-calc-reference, "Planner-service plan rules"):
- Bucket starts full at the start of day 1: L = TAW = 70 mm.
- Trigger: irrigate when L_pre < 0.5 x TAW = 35 mm (strictly below).
- Day step: L_pre = min(TAW, L_prev + rain - ETc). If L_pre < trigger, need = TAW - L_pre and end level = TAW. Otherwise need = 0 and end level = L_pre.
- ETc = 7 mm/day, rain = 0.

| Day | L_prev | L_pre | < 35? | Need (mm) | End level (mm) |
|---|---|---|---|---|---|
| 1 | 70 | 63 | no | 0 | 63 |
| 2 | 63 | 56 | no | 0 | 56 |
| 3 | 56 | 49 | no | 0 | 49 |
| 4 | 49 | 42 | no | 0 | 42 |
| 5 | 42 | 35 | no (equal, not below) | 0 | 35 |
| 6 | 35 | 28 | yes | 70 - 28 = 42 | 70 |

## Answer
- First irrigation: **day 6**.
- Amount applied: **42 mm** (refill to full: 70 - 28).
- Bucket level at the end of day 6: **70 mm** (full).

Note: day 5 lands exactly on the 35 mm trigger. The rule is "would fall below", so equality does not irrigate. If the trigger were "at or below", the first irrigation would be day 5 (need 35 mm). I followed the skill's strict rule.
