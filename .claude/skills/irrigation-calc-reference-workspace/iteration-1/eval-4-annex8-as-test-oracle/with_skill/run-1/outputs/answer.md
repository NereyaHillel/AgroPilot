**Short answer: don't use Annex 8 as a numeric day-by-day oracle. Use it as a structural oracle and for a few hand-built checks.**

## Why not numbers
- Annex 8 is a **dual-Kc** example ("Calculation example for applying the dual Kc procedure"): Kc = Kcb + Ke, with an evaporation layer (TEW 22, REW 8, initial De 18 mm), Kr, few, fc (Eqs. 69-79), and Kc adj = Ke + Ks Kcb (Eq. 80). Our planner is single Kc (Eq. 56/58, stressed Eq. 81). Its daily Kc, ETc and depletion columns will never match ours.
- It's **dry beans in Kimberly (1974)**, not tomato or pepper. The Kcb values (0.15 / 1.1 / 0.25, adjusted to 1.13 / 0.23), stage lengths 25/25/30/20, h 0.4 m and the Kimberly weather all differ from our presets.
- **Little published daily output.** Figure 8.1 shows only 15-27 May. After that there's just the Figure 8.3 graph (about nine irrigation markers, read off approximately). The text gives no total depth, count or dates. Most of the season has nothing to assert against.

## What you can compare against
1. **Order of the daily steps** (Box 8.1 columns). Kc from Eq. 66, then ETc, a first-estimate depletion (Eq. 85, unstressed), the trigger, DP (Eq. 88), Ks (Eq. 84), Kc adj, then corrected end-of-day depletion (Eq. 85), clamped by Eq. 86.
2. **Trigger and refill shape.** If first-estimate depletion > allowable depletion, the next morning's net irrigation equals that depletion (refill to FC), and no irrigation is applied on day 1. Gross depth = net / fw. Only the field-average **net** depth enters Eq. 85. The one checkable data point: 25.3 mm net decided at the end of 22 May, applied on 23 May as 50.6 mm over fw 0.5.
3. **Eq. 66 interpolation shape**, using Box 8.1's day-of-year logic.
4. **Rain/DP handling**: early-morning wetting, runoff = 0, excess drains as DP the same day.

The better numeric oracle for single Kc is **Ch. 8 Example 37** (a full-grown tomato, Zr 0.8 m, p 0.40, single Kc, Ks from start-of-day depletion). `daily_soil_step` already follows it.

## Watch out for
- **Which depletion feeds Ks.** Annex 8 footnote 11 uses depletion *after* that morning's rain or irrigation. Example 37, and `daily_soil_step`, use start-of-day depletion (the previous day's end). Same Eq. 84, different input, different numbers. Pick one per test and say which.
- **Trigger operator.** The formula is `IF(AG > AF, ...)` (strict), but the text says "greater than or equal to RAW". `irrigation_decision` uses `>`.
- **p is MAD, not adjusted.** Annex 8 sets p = MAD (70% initial stage, 45% after) and doesn't apply p = p(Table 22) + 0.04(5 - ETc). `daily_soil_step` does adjust p, so turn that off or expect differences.
- **Root growth.** Annex 8 grows Zr with Kcb (Eq. 8-1/8-2, 0.2 to 0.8 m). The single-Kc chapters give no season-long rule, and our presets use a fixed Zr (0.7 tomato, 0.5 pepper). Growing roots also changes TAW every day.
- **fw.** Annex 8 uses fw for evaporation (few) and for gross depth. In single Kc the only FAO-56 use of fw is Kc ini x fw (Eq. 60). Don't carry its fw into Kc mid/end.
- **Box 8.1 typos.** "014" means O14, "16" means I6, "AU 4" means AL14. Footnote 9 calls AK the end-of-day depletion, but AK is Kc adj and **AL** is the depletion. Figure 8.1 shows Kcb end 0.23, but 0.25 < 0.45, so under the Eq. 65 rule it shouldn't have been adjusted.
- **Two different rule sets in our code.** The FAO-style functions (`daily_soil_step`, `irrigation_decision`) are the only ones Annex 8 says anything about. The actual plan rule, `bucket_day`, is a product choice: trigger below 50% TAW, refill to TAW, no Ks, no p adjustment, a per-day cap that splits refills over days. Annex 8 can't validate `bucket_day`. Test that against its own spec.
- **Rounding.** The source specifies none. Compare with a tolerance, not exact equality.

**My suggestion:** use Annex 8 tests to check the structure (step order, trigger/refill, gross = net/fw, Eq. 66 shape, DP clamp). For numeric single-Kc tests, reproduce Ch. 8 Example 37. Write a few hand-computed tomato/pepper cases from `crops.py` presets, with each equation number cited in the test.

Sources: `services/planner-service/docs/research/fao56.md` (sections 3-5), `services/planner-service/irrigation.py`.
