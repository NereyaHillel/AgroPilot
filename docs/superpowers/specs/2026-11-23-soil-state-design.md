# Soil state before the plan (design)

## Intent and why
The planner assumes the soil bucket is full at the start of day 1. That is often wrong, and it delays the first irrigation on a dry field. The farmer says how wet the soil was the day before, and the plan starts from that level.

## Goals
- The farmer picks **Dry**, **Half** or **Wet** on the plot page, and the plan starts from that level.
- There is no default. Until the farmer chooses, no plan is shown.

## Non-goals
- Saving the choice per plot or across visits beyond the URL.
- A numeric moisture input.
- Changing the bucket rules after day 1.

## Anti-goals
- Silently falling back to "full" when the choice is missing, in either the frontend or the planner.

## Constraints
- planner-service plan rules and the irrigation-calc-reference skill apply: TAW = available_water_mm_per_m x Zr, trigger at 0.5 x TAW, no rounding in the engine.
- The frontend is Next.js with a changed API surface: read `node_modules/next/dist/docs/` before writing page code (see services/frontend/AGENTS.md).

## Approaches
1. **Query parameter end to end (picked as my recommendation).** The control writes `?soil=dry|half|wet` to the page URL. The server page passes it to the planner as `soil_state`. It stays stateless, survives refresh and can be shared.
2. Client-side state with a client fetch of the plan. This needs a client data layer the app doesn't have, and the choice is lost on refresh.
3. Store the choice per plot in the registry. This needs a schema and migration, and the answer goes stale daily, so it's the wrong place for it.

## Design
**Planner**
- `GET /v1/plots/{id}/plan` takes a **required** `soil_state` of `dry`, `half` or `wet`. A missing or unknown value returns a 422 problem response (the planner's existing error shape).
- Starting level: dry = 0, half = 0.5 x TAW, wet = TAW.
- `bucket_day` floors `level_pre` at 0, so a dry start refills to full on day 1 without adding that day's ET on top. This is my call and is flagged for the builder.
- The existing planner tests assumed a full start and no parameter. They are updated to pass `soil_state=wet`.
- New tests: each state, the missing and invalid values, and the dry-start floor. Add Case 6 to the irrigation reference: tomato, sand 83 mm/m, TAW 58.1, dry start, day 1 need = 58.1 mm.

**Frontend**
- `getPlan(plotId, soilState)` sends the parameter.
- The plot page reads `searchParams.soil`.
  - Missing or invalid: show a prompt, "How wet was the soil yesterday?", with the control and no plan.
  - Valid: show the plan, with the control above the sign plate and the chosen option marked.
- The control is a three-button segmented control, **Dry · Half · Wet**, built from the existing `Button` and the sign-plate styling. The buttons are links to `?soil=...`, so there is no client JS.

## Left to the builder
Exact wording and visual styling inside the existing design, the accessible labelling of the control (radio-group semantics), and the label text for each option.
