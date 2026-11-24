# Annex 8 as a test oracle for planner-service

**Short answer:** it doesn't work well as an end-to-end day-by-day oracle. Annex 8 is a **dual-Kc (Kcb + Ke) example for dry beans** (Kimberly, 1974), not a single-Kc tomato or pepper example. Its daily Kc, ETc, depletion and irrigation columns all depend on the evaporation-layer model (Ke, TEW/REW, few) and on a root depth that grows each day. Our engine has neither. Use it to check **individual formulas and the order of steps**, not to match its numbers row for row. (Source: `services/planner-service/docs/research/fao56.md` section 4. I did not re-check the FAO pages for this answer.)

## What you can compare against

- **The Kc curve shape (Eq. 66).** Linear in development and late season, flat in initial and mid. This checks the logic of `kc_for_day`, but against **Kcb** values (0.15 / 1.13 / 0.23, stages 25/25/30/20), not Kc. The day numbering also differs: Annex 8 counts by day of year (planting at J 142) and goes back to Kcb ini after harvest. We use a 1-based season day and hold the end value after the season. Expect differences at stage boundaries and outside the season.
- **The Ks formula (Eq. 84) and the water balance (Eq. 85, 86, 88).** The structure is the same: rain and irrigation in the morning, ET, depletion clamped to 0..TAW, deep percolation from the excess. Annex 8 also gets Ks from the depletion after the morning's water, which matches `daily_soil_step`. Feed the spreadsheet's own ETc and Zr for a day into it and the depletion, deep percolation and Ks should match. This holds only if you set p to the Annex value. Annex 8 uses **p = MAD (0.70 in the initial stage, then 0.45), with no ETc adjustment**, so `adjusted_p` cannot be checked here.
- **The trigger and refill rule.** If first-estimate end-of-day depletion > allowable depletion, irrigate the next morning with that depth (a refill to field capacity). Note that the text says ">=" but the cell formula uses ">". This matches `irrigation_decision`.

## What you can't compare against

- **The production plan (`build_plan` / `bucket_day`).** This is the main catch. The `/plan` endpoint doesn't use the FAO-56 stress model at all. It irrigates the same day when the level would fall below **0.5 × TAW** and refills to TAW. It has no Ks and no p adjustment, it caps a day's water at 24 h of drip run time, and it starts from the farmer's dry/half/wet answer. Annex 8 can only check the FAO-56 helper functions in `irrigation.py`, not what the endpoint returns.
- **Daily Kc and ETc values.** Annex 8 uses Kc = Kcb + Ke, and Ke jumps after each wetting. Single Kc averages that effect, so ETc will differ on most days.
- **TAW and RAW.** Annex 8's Zr grows from 0.2 to 0.8 m in step with Kcb (Eq. 8-1). Ours is fixed (0.7 m for tomato, 0.5 m for pepper).
- **Drip.** Annex 8 uses fw = 0.5 for evaporation from the wetted area and divides the gross application by fw. Our engine only has `drip_kc_ini = fw × Kc ini`, which `build_plan` doesn't call. Nothing here covers tomato or pepper on drip.
- **Totals.** The text doesn't state the season's total irrigation or the irrigation dates. Figure 8.1 shows only rows for 15-27 May (the first net irrigation is 25.3 mm, applied on 23 May as 50.6 mm over fw 0.5). The nine irrigations in Figure 8.3 are read off a graph and are approximate.

## Watch out for

1. **Transcription.** The spreadsheet exists only as three GIF images, and Box 8.1 has typos ("014" for O14, "AU 4" for AL14, and footnote 9 points to the wrong column). Check every number you copy against the image.
2. **Rounding.** The printed values are rounded, so compare with a tolerance (about ±0.1 mm). Use the spreadsheet's own intermediate values (ETc, Zr, p) as inputs; don't recompute them upstream.
3. **Conventions.** These are where a mismatch will show up: day 1 vs day 0, which depletion Ks uses, whether rain arrives before ET, the strict ">" trigger, irrigation being off on the first day and after mid-late season, and runoff = 0.
4. **Better single-Kc oracles.** Chapter 8 Examples 37/38 are single-Kc water balances (Example 37 is a full-grown tomato, Zr 0.8 m, p 0.40). They are a closer fit for `daily_soil_step`. For our own crops and plan rules, hand-calculated cases are the honest oracle.
