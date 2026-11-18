# Bucket model: first irrigation

Answered from general knowledge (FAO-56 style bucket). I did not read the planner code, so the trigger rule below is an assumption.

## Assumptions
- Bucket capacity is 70 mm and it starts full (70 mm).
- Loss is 7 mm/day with no rain.
- Irrigation triggers when depletion exceeds the readily available water. I assumed RAW = 50% of capacity = 35 mm, so the bucket level must drop below 35 mm.
- When it triggers, the planner refills to full capacity, and the day's loss is applied before the irrigation decision.

## Daily levels (end of day, before irrigation)
| Day | Level (mm) | Depletion (mm) |
|---|---|---|
| 1 | 63 | 7 |
| 2 | 56 | 14 |
| 3 | 49 | 21 |
| 4 | 42 | 28 |
| 5 | 35 | 35 (equals RAW, not above it) |
| 6 | 28 | 42 (exceeds RAW) |

## Answer
- First irrigation day: day 6.
- Amount applied: 42 mm (refill from 28 mm to 70 mm).
- Bucket level at the end of day 6: 70 mm.

## Caveat
If the planner triggers when depletion is greater than or equal to RAW (a non-strict comparison), it would irrigate on day 5 and apply 35 mm. The 50% threshold is also an assumption. A different threshold would change the day and the amount.
