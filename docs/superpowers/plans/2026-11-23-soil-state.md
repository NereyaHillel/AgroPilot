# Soil State Before the Plan Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The farmer chooses Dry, Half or Wet for the soil the day before, and the plan starts from that bucket level. There is no default.

**Architecture:** planner-service takes a required `soil_state` query parameter and maps it to the day-1 starting level. The Next.js plot page reads `?soil=` from the URL, passes it to the planner, and shows a chooser instead of a plan when it is missing or invalid.

**Tech Stack:** FastAPI + pytest (planner-service), Next.js 16 / React 19 / Tailwind (frontend, no test runner: verify with `npm run lint` and `npm run build`).

**Spec:** `docs/superpowers/specs/2026-11-23-soil-state-design.md`

## Global Constraints

- Starting level: dry = 0.5 x TAW (at the trigger), half = 0.75 x TAW, wet = TAW. (Revised 2026-11-24; this plan originally used dry = 0, half = 0.5 x TAW.)
- `soil_state` is required. A missing or unknown value returns 422 `VALIDATION` (problem+json). No fallback to full anywhere.
- No rounding in the engine; API rounding unchanged (mm / litres / minutes 2 decimals).
- Frontend: read `services/frontend/node_modules/next/dist/docs/` before writing page code (see `services/frontend/AGENTS.md`).
- Registry-service is untouched. Do not store the choice.

## Review Focus

- `?soil=` repeated (`?soil=dry&soil=wet`) arrives as an array: treat it as invalid, show the chooser.
- `?soil=DRY` (wrong case): invalid, show the chooser. No guessing.
- Dry start with rain on day 1: level after rain and ET is still floored at 0 and capped at TAW.
- Dry start on a day with ET larger than TAW: need is exactly TAW, never TAW + ET.
- Planner failure with a valid choice still shows the existing problem notice, with the chooser kept so the farmer can switch.

---

### Task 1: Planner engine and API take `soil_state`

**Files:**
- Modify: `services/planner-service/irrigation.py` (`bucket_day`, add `START_FRACTION`)
- Modify: `services/planner-service/plan.py` (`build_plan`)
- Modify: `services/planner-service/schemas.py` (add `SoilState`)
- Modify: `services/planner-service/routers/plan.py`
- Test: `services/planner-service/tests/test_bucket.py`, `tests/test_plan_api.py`

**Interfaces:**
- Produces: `schemas.SoilState` (`StrEnum`: `dry`, `half`, `wet`);
  `irrigation.START_FRACTION: dict[str, float]` = `{"dry": TRIGGER_FRACTION, "half": 0.75, "wet": 1.0}` (revised 2026-11-24);
  `build_plan(plot, soil, emitter, forecast, days, soil_state: SoilState) -> dict`.
- Consumes: existing `bucket_day(level_prev, taw, rain, etc_mm) -> BucketDay`.

- [ ] **Step 1: Write failing tests**

In `test_bucket.py`:
```python
def test_empty_bucket_floors_level_so_need_is_exactly_taw():
    # tomato, sand 83 mm/m, TAW 58.1, empty bucket (level 0), ETc 5.75
    day = bucket_day(0.0, 58.1, 0.0, 5.75)
    assert day.need_mm == pytest.approx(58.1)
    assert day.level_end == pytest.approx(58.1)

def test_empty_bucket_with_et_larger_than_taw_still_needs_exactly_taw():
    assert bucket_day(0.0, 58.1, 0.0, 100.0).need_mm == pytest.approx(58.1)

def test_empty_bucket_rain_is_counted_after_the_floor_and_capped():
    assert bucket_day(0.0, 58.1, 20.0, 5.75).level_end == pytest.approx(14.25)
```
In `test_plan_api.py`: change `get_plan` to take `soil_state="wet"` and send it as a param; add tests:
```python
def test_soil_state_is_required(client):
    assert_problem(client.get(f"/v1/plots/{PLOT_ID}/plan"), 422, "VALIDATION")

@pytest.mark.parametrize("value", ["", "full", "DRY", "0.5"])
def test_unknown_soil_state_is_422(client, value):
    body = assert_problem(get_plan(client, soil_state=value), 422, "VALIDATION")
    assert "soil_state" in body["detail"]

def test_dry_start_is_at_the_trigger_and_irrigates_on_day_1(client):
    # dry = 0.5 x TAW = 29.05; minus ETc 5.75 = 23.3 < trigger, so need 34.8 mm
    # (revised 2026-11-24; with the later 24 h/day cap the endpoint returns 24 mm on day 1)
    day1 = get_plan(client, soil_state="dry").json()["days"][0]
    assert (day1["need_mm"], day1["litres"], day1["run_minutes"]) == (34.8, 52200.0, 2088.0)

def test_half_start_is_three_quarters_full_and_does_not_irrigate(client):
    # half = 0.75 x TAW = 43.575; minus ETc 5.75 = 37.825, above the trigger 29.05
    day1 = get_plan(client, soil_state="half").json()["days"][0]
    assert (day1["need_mm"], day1["run_minutes"]) == (0, 0)
```
`test_seven_day_plan_matches_hand_calculation` and the other existing plan tests keep their numbers via the `wet` default in the helper. Check the `get_plan` helper is also used in `test_upstream_errors.py`, which should pass `soil_state=wet` too.

- [ ] **Step 2: Run to verify they fail**

Run: `cd services/planner-service && uv run pytest -q`
Expected: new tests FAIL (floor missing, parameter ignored), nothing else broken yet.

- [ ] **Step 3: Implement**

`bucket_day`: `level_pre = max(0.0, min(taw, level_prev + rain - etc_mm))`; update its docstring. Add `START_FRACTION` beside `TRIGGER_FRACTION`. `schemas.SoilState(StrEnum)`. `build_plan` sets `level = START_FRACTION[soil_state] * taw` in place of `level = taw` and drops its "starts full" comment. The router adds `soil_state: Annotated[SoilState, Query()]` (no default) and passes it on. FastAPI's validation already yields 422 `VALIDATION` via the existing handler.

- [ ] **Step 4: Run to verify all pass**

Run: `cd services/planner-service && uv run pytest -q`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add services/planner-service
git commit -m "feat(planner): start the bucket from a required soil_state"
```

### Task 2: Frontend chooser and page wiring

**Files:**
- Create: `services/frontend/src/lib/soil-state.ts`, `services/frontend/src/components/soil-state-picker.tsx`
- Modify: `services/frontend/src/lib/planner.ts`, `services/frontend/src/app/plots/[id]/page.tsx`

**Interfaces:**
- Produces: `lib/soil-state.ts` exports `type SoilState = "dry" | "half" | "wet"`, `SOIL_STATES: readonly SoilState[]` (in order dry, half, wet), `soilLabel(s: SoilState): string` ("Dry", "Half", "Wet"), `parseSoilState(value: string | string[] | undefined): SoilState | null` (exact lowercase match only; arrays, other cases and empty return `null`).
- Produces: `<SoilStatePicker plotId: string selected: SoilState | null />`, a server component. Renders a `role="radiogroup"` labelled "Soil the day before"; each option is a link to `plotHref(plotId)` + `?soil=<value>` (check `lib/format.ts` for `plotHref`), styled like `Button` (`buttonVariants`) with the selected one filled (`aria-checked`) and the others outline.
- Changes: `getPlan(plotId: string, soilState: SoilState): Promise<Plan>` appends `&soil_state=<value>`.

- [ ] **Step 1: Implement `lib/soil-state.ts` and the picker**, following the existing `sign-plate` and `buttonVariants` styling. Large touch targets (field use on a phone).
- [ ] **Step 2: Wire the page.** `PlotPage` reads `searchParams` from `PageProps<"/plots/[id]">`, parses `soil`. When `null`, render under the plot header: the prompt "How wet was the soil yesterday?" and `<SoilStatePicker selected={null} />`, with no `PlanSection`. When valid, render the picker above the plan inside the Suspense boundary's sibling (so it shows at once) and pass `soilState` to `PlanSection`. The existing problem notices stay, and the picker is outside them so it remains on screen.
- [ ] **Step 3: Verify**

Run: `cd services/frontend && npm run lint && npm run build`
Expected: both succeed.
Then run the app with the `run` skill: with all three services up, check `/plots/<id>` (chooser only, no plan), `?soil=dry` (plan starting with watering today), `?soil=wet` (matches the old plan), `?soil=DRY` and `?soil=dry&soil=wet` (chooser).

- [ ] **Step 4: Commit**

```bash
git add services/frontend
git commit -m "feat(frontend): ask for the soil state before showing the plan"
```

### Task 3: Docs

**Files:**
- Modify: `.claude/skills/irrigation-calc-reference/SKILL.md` (plan rules table: "Start" row; add Case 6 from Task 1's first test; clarify the floor in "Day step")
- Modify: `services/planner-service/README.md` / `OVERVIEW.md` (endpoint parameter), `services/frontend/OVERVIEW.md` (the chooser), `CHANGELOG.md`

- [ ] **Step 1:** Replace "bucket full at the start of day 1" with "starts at the farmer's choice: dry 0.5 x TAW (at the trigger), half 0.75 x TAW, wet TAW (required)"; add the dry-start case (dry 29.05 mm, ETc 5.75, need 34.8 mm) (revised 2026-11-24); note `L_pre` is floored at 0.
- [ ] **Step 2:** Document `soil_state` in the planner docs and the chooser in the frontend overview; add a CHANGELOG entry in the file's existing style.
- [ ] **Step 3: Commit**

```bash
git add .claude/skills/irrigation-calc-reference/SKILL.md services/planner-service services/frontend CHANGELOG.md
git commit -m "docs: soil state rule, case 6 and endpoint parameter"
```
