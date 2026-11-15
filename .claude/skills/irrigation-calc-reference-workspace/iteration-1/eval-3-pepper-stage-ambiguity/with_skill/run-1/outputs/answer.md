# Bell pepper, Mediterranean, mid-April transplant (FAO-56 Table 11/12, single Kc)

Source: `services/planner-service/docs/research/fao56.md` (Tables 11, 12; Eq. 66). The skill says to decide where FAO-56 gives options, so each choice is stated below.

## Values to load

| Parameter | Value | Basis |
|---|---|---|
| Row used | Sweet pepper (bell), Europe and Mediterranean, plant date Apr/Jun | Table 11. It is the only pepper row for this region and planting window. The other pepper row is October, arid region. |
| Initial stage | **30 days** | Choice, see below. |
| Development stage | **35 days** | Table 11 |
| Mid stage | **40 days** | Table 11 |
| Late stage | **20 days** | Table 11 |
| Total | **125 days** | Matches the printed total of 125 |
| Kc ini | **0.6** | Solanum group row. The per-crop cell is blank, so I applied the group value to pepper (an inference in the source notes). |
| Kc mid | **1.05** | Table 12, unstaked, h = 0.7 m |
| Kc end | **0.90** | Table 12, a single value, no choice needed |

### Choices made
- **Initial stage 25 vs 30: I chose 30.** Table 11 prints "25/30" with no explanation. The printed total of 125 days equals 30+35+40+20. With 25 the sum is only 120. So 30 is the value consistent with the table. This is my inference, and the planner should let the grower override it with a local observation.
- **Table 11 variant:** Europe and Mediterranean (Apr/Jun planting). Stage lengths count from transplanting, which is the day-1 reference I used.
- **Day 1 of the count:** transplanting day is day 1, so day 20 is the 20th day of the initial stage and day 31 is the first development day. The source does not fix this, so it is my choice.
- **Not applied:** no climate adjustment (Eq. 62/65) because no u2 or RHmin were given, so the tabulated sub-humid values are loaded as-is. No staking uplift (footnote 2: Kc mid 1.15 if staked to 1.5-2 m). No drip scaling of Kc ini (Eq. 60, fw 0.3-0.4 would give about 0.18-0.24, or 0.42 as in the source's Example 26). Kc ini stays at the table value 0.6, since FAO-56 scales only Kc ini for drip and says nothing about Kc mid/end. If the planner models drip, flag this as a separate decision.

## Kc on day 20 and day 50 (Eq. 66)

Stage boundaries: initial days 1-30, development days 31-65, mid days 66-105, late days 106-125.

- **Day 20: Kc = 0.60.** It falls in the initial stage, where Kc is flat at Kc ini.
- **Day 50: Kc = 0.857 (about 0.86).** It falls in the development stage:
  Kc = 0.6 + (50 - 30)/35 x (1.05 - 0.6) = 0.6 + 0.5714 x 0.45 = 0.857.

Sensitivity: if the grower's local initial stage is 25 days, day 20 is still 0.60, but day 50 becomes 0.6 + (50-25)/35 x 0.45 = 0.921 (about 0.92). Day 50 is therefore sensitive to the 25 vs 30 choice and day 20 is not.
