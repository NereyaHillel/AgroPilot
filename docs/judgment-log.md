# Judgment log

## 1. Blank names

- **Problem:** The spec says farm names can't be empty but says nothing about plot names.
- **My answer:** Farm and plot names can't be empty or whitespace-only.
- **Reason:** Blank names are meaningless, and one rule for both names keeps things consistent.

## 2. What "today" means

- **Problem:** The spec doesn't define "today" for the rule that `planting_date` can't be in the future.
- **My answer:** "Today" is the UTC date.
- **Reason:** UTC gives the same date on every server.

## 3. Unknown request fields

- **Problem:** The spec doesn't say what to do with fields the API doesn't recognize.
- **My answer:** Reject them with 422.
- **Reason:** A typo in a PATCH body would otherwise return 200 and silently change nothing.

## 4. Moving a plot to another farm

- **Problem:** The spec doesn't say whether PATCH can change a plot's `farm_id`.
- **My answer:** Yes, if the new farm exists and the plot name is unique there.
- **Reason:** The spec says PATCH updates any field provided.

## 5. List order

- **Problem:** The spec doesn't define the order of list responses.
- **My answer:** Sort by name, then id.
- **Reason:** It gives a stable, predictable order.

## 6. Plot-name case sensitivity

- **Problem:** The spec doesn't say whether plot-name uniqueness is case-sensitive.
- **My answer:** Case-sensitive.
- **Reason:** It matches the database's UNIQUE index, so the app check and the database always agree, even in a race.

## 7. Request body that isn't valid JSON

- **Problem:** Malformed JSON returned 422, but invalid UTF-8 returned 400 (FastAPI's default).
- **My answer:** Both return `422 VALIDATION` with `body: could not be read as JSON`.
- **Reason:** Both are bad request bodies, and the spec maps validation errors to 422. A test pins FastAPI's message text, so an upgrade that changes it fails loudly.

## 8. Where a new plot's id comes from

- **Problem:** `plots` keeps `id` as its primary key, so every new plot needs one. The client could send it, or the server could generate it.
- **My answer:** The server generates the id and returns it in the POST response.
- **Reason:** Routes use `/v1/plots/{id}`, and the original design already generated ids on the server.

## 9. Farm area endpoint

- **Problem:** The spec doesn't define `GET /v1/farms/{id}/area`: its response body, or what a farm with no plots returns.
- **My answer:** It returns `{"area_m2": <sum of the farm's plot areas>}`. A farm with no plots returns `200` with `area_m2` of `0`. An unknown farm returns `404`.
- **Reason:** The field reuses the plot field name, so the unit is clear and nothing else is exposed. Zero is the true sum of no plots, and an existing farm with no plots is a valid state, like an empty list.

## 10. Planner: when to irrigate (trigger level)

- **Problem:** The task says irrigate when the level would fall below half the bucket. FAO-56 Table 22 gives p = 0.40 for tomato and 0.30 for bell pepper, and the first version of the skill used those.
- **My answer:** Half of the bucket for both crops. The skill now states this, and TAW is `available_water_mm_per_m x root depth` because registry stores that, not field capacity and wilting point.
- **Reason:** It is the rule written in the task, and the numbers in the plan must follow the skill. The difference from Table 22 is deliberate and documented.

## 11. Planner: where the bucket starts

- **Problem:** Neither registry-service nor weather-service knows today's soil moisture.
- **My answer:** The bucket is full at the start of day 1.
- **Reason:** It is the only starting level that needs no invented data. The cost is that a plan often says "no need" in its first days, and it is stated in the README.

## 12. Planner: crop parameters

- **Problem:** FAO-56 leaves open the stage lengths variant, tomato Kc end (0.70 to 0.90), pepper initial stage ("25/30"), Kc ini per crop (blank in Table 12) and the root depth.
- **My answer:** Tomato: Table 11 Mediterranean Apr/May, 30/40/45/30 days, Kc 0.6 / 1.15 / 0.80, Zr 0.7 m. Bell pepper: Europe and Mediterranean, 30/35/40/20 days (30 so the total matches the printed 125), Kc 0.6 / 1.05 / 0.90, Zr 0.5 m. All in `crops.py`.
- **Reason:** Each value is inside the range FAO-56 gives, the Zr values are the small end that Table 22 recommends for scheduling, and one table is easy to change.

## 13. Planner: how much one irrigation applies

- **Problem:** An irrigation could refill to full or only to the trigger.
- **My answer:** Refill to full (Annex 8 rule).
- **Reason:** Fewer, longer runs. Known consequence: with a half-bucket trigger the net depth is large (30 to 60 mm), so on slow emitters one run can last more than 24 hours. The plan reports it as calculated and does not cap it. Needs a decision before this reaches growers.

## 14. Planner: plots past the end of the season

- **Problem:** A plot whose planting date is older than the crop's season (all four seed plots are) has no Kc on the growth curve.
- **My answer:** The Kc holds its end value after the last stage day.
- **Reason:** A plan with a sensible value beats a 422 for plots that registry accepts. Not confirmed by the user, so it is listed as open in the skill.

## 15. Planner: stale forecast with fewer days

- **Problem:** weather-service may return fewer days than asked when its forecast is stale. FR-2.13 wants a plan, FR-2.9 wants `days` days.
- **My answer:** The plan covers the days the forecast has, each marked `stale: true`. No day is invented.
- **Reason:** A shorter plan is honest. Filling the rest would mean made-up weather, and a 503 would withhold a usable plan. Not confirmed by the user.

## 16. Planner: error codes

- **Problem:** FR-2.14 needs a code for an upstream failure, and a 500 needs one too.
- **My answer:** 503 uses `UPSTREAM_UNAVAILABLE` with `Retry-After`, and the detail names `registry-service` or `weather-service`. An unexpected error is 500 with `INTERNAL`.
- **Reason:** `UPSTREAM_UNAVAILABLE` comes from the task. `UNAVAILABLE` (registry's 500 code) would be misleading for a bug, so planner-service uses its own code.
