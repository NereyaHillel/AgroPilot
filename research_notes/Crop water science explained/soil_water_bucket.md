# Soil water balance, the "soil bucket" and when to irrigate (FAO-56 and the project's half rule)

Reading method and limits (read first): FAO pages were read through WebFetch, which returns a model-made summary, not raw text. FAO's equations are images. I downloaded and visually read the image of Eq. 84 (x0490e2w.gif). Eqs. 82, 83, 85, 86, 87, 88 and the p-adjustment were taken from the fetched text (the fetch tool rendered them as text) and agree with the project notes. Anything marked "Inference" is my own reasoning, not source text. Anything marked "NOT VERIFIED" has no source. FAO-56 = Allen et al. (1998), FAO Irrigation and Drainage Paper 56. FAO URLs redirect from www.fao.org/3/ to www.fao.org/4/.

Source URLs used:
- Ch. 8 (ETc under soil water stress): http://www.fao.org/4/x0490E/x0490e0e.htm
- Ch. 7 (Table 19, soil water): http://www.fao.org/4/x0490E/x0490e0c.htm
- Eq. 84 image: http://www.fao.org/4/x0490E/x0490e2w.gif
- Project notes (a lead, not proof): /home/nereya/AgroPilot/services/planner-service/docs/research/fao56.md, /home/nereya/AgroPilot/.claude/skills/irrigation-calc-reference/SKILL.md, /home/nereya/AgroPilot/services/planner-service/irrigation.py

## 1. Soil water terms in plain language, and typical available water by soil

### Takeaway
Soil holds water between two useful limits: field capacity (the most it keeps after extra water drains away) and permanent wilting point (below this plants cannot extract water). The gap between them is plant-available water, roughly 50-110 mm per metre for sand and 130-180 mm per metre for loam in FAO's Table 19.

### Cited Findings
- Field capacity (FC): water a well-drained soil holds against gravity, i.e. what is left once downward drainage has largely stopped — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Wilting point (WP): the water content at which plants permanently wilt and uptake stops — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Water above field capacity (after heavy rain or irrigation) is assumed to be lost the same day by deep percolation, so root-zone storage is capped at field capacity in the model — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Available water is thetaFC minus thetaWP (volumetric, m3/m3). Multiplying by 1000 gives mm of water per metre of soil depth (1 m3/m3 over 1 m depth = 1000 mm); this is the factor inside Eq. 82 — [FAO-56 Ch. 8, Eq. 82](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Table 19 (Ch. 7), typical thetaFC / thetaWP / difference (m3/m3). Sand 0.07-0.17 / 0.02-0.07 / 0.05-0.11. Loamy sand 0.11-0.19 / 0.03-0.10 / 0.06-0.12. Sandy loam 0.18-0.28 / 0.06-0.16 / 0.11-0.15. Loam 0.20-0.30 / 0.07-0.17 / 0.13-0.18. Silt loam 0.22-0.36 / 0.09-0.21 / 0.13-0.19. Silt 0.28-0.36 / 0.12-0.22 / 0.16-0.20. Silt clay loam 0.30-0.37 / 0.17-0.24 / 0.13-0.18. Silty clay 0.30-0.42 (printed "0-30", likely a typo) / 0.17-0.29 / 0.13-0.19. Clay 0.32-0.40 / 0.20-0.24 / 0.12-0.20 — [FAO-56 Ch. 7, Table 19](http://www.fao.org/4/x0490E/x0490e0c.htm)
- In mm of water per metre of soil (difference x 1000): sand 50-110, loam 130-180, silty clay loam 130-180, clay 120-200 — arithmetic on [Table 19](http://www.fao.org/4/x0490E/x0490e0c.htm)
- Table 19 has no row called "clay loam"; the nearest are "Silt clay loam" and "Clay" — [FAO-56 Ch. 7, Table 19](http://www.fao.org/4/x0490E/x0490e0c.htm)
- Project registry soil catalogue (as given by the requester, not re-checked against the registry code): sand 83, loam 175, clay-loam 200 mm per metre. The planner uses these directly for the bucket size instead of theta values — [irrigation-calc-reference SKILL.md](/home/nereya/AgroPilot/.claude/skills/irrigation-calc-reference/SKILL.md)

### Inferences
- Sand 83 and loam 175 sit inside Table 19's ranges (50-110 and 130-180). Clay loam 200 is above the 130-180 range of the nearest Table 19 row (silt clay loam) and at the top of the clay range (120-200); it is plausible but not an FAO "typical" value. These are typical ranges only; real soils vary, which the table itself signals by giving ranges.
- Plain picture: sand is a small, leaky bucket (water drains quickly, little is held); loam and clay-loam hold much more usable water per metre.

### Gaps
- Saturation (all pores full of water) is not defined in the FAO Ch. 7/8 pages I read, and no FAO number is given for it. NOT VERIFIED from FAO; it is only general soil-science knowledge: saturation is above field capacity, and the excess drains within about a day or so. Do not quote a figure for it from these notes.
- FAO's Table 19 page gives no definition of field capacity beyond the symbol; the Ch. 8 definitions above are the ones to use.
- I did not verify the registry soil values in the registry code.

## 2. Root depth and bucket size

### Takeaway
The bucket holds (available water per metre) x (root depth in metres), because plants can only take water from the soil their roots reach. FAO gives maximum root depth 0.7-1.5 m for tomato and 0.5-1.0 m for bell pepper, and says the smaller values suit irrigation scheduling; the project fixes 0.7 m (tomato) and 0.5 m (bell pepper), which are the bottom of those ranges.

### Cited Findings
- TAW = 1000 (thetaFC - thetaWP) Zr; TAW in mm, theta in m3/m3, Zr (rooting depth) in m — [FAO-56 Ch. 8, Eq. 82](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Table 22: tomato Zr 0.7-1.5 m, p 0.40; sweet pepper (bell) Zr 0.5-1.0 m, p 0.30 — [FAO-56 Ch. 8, Table 22](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Table 22 footnote 1: smaller Zr values may be used for irrigation scheduling; larger values for modelling soil water stress or for rainfed conditions — [FAO-56 Ch. 8, Table 22 footnote 1](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Project rule: Zr fixed at 0.7 m (tomato) and 0.5 m (bell pepper); TAW = available_water_mm_per_m x Zr — [SKILL.md, Planner-service plan rules](/home/nereya/AgroPilot/.claude/skills/irrigation-calc-reference/SKILL.md)
- Project bucket sizes follow by multiplication: tomato 0.7 m: sand 58.1 mm, loam 122.5 mm, clay loam 140 mm. Bell pepper 0.5 m: sand 41.5, loam 87.5, clay loam 100 mm — arithmetic on the project values above. (58.1 matches the skill's case 4.)
- FAO describes Zr as growing during the season and gives no general growth curve in Ch. 8 (Example 38 uses 0.30 to 0.35 m over 10 days; Annex 8 grows Zr in proportion to Kcb) — [project notes fao56.md sec. 3-4](/home/nereya/AgroPilot/services/planner-service/docs/research/fao56.md) (secondhand; I did not re-read Example 38 or Annex 8)

### Inferences
- Why the smaller depth for scheduling (FAO gives the rule, not the reason): the smaller depth is the zone where most roots and the easiest-to-reach water are, so it gives a smaller bucket and a more conservative (earlier) irrigation; using the full maximum depth would count deep water that the crop may not reliably reach. A fixed depth also ignores young plants having shallower roots than the maximum, so early in the season the real bucket is smaller than the planner's.

### Gaps
- Table 22's tomato range is for the crop's maximum depth; I did not find an FAO statement of why the 0.7 / 0.5 m project values were chosen. They are the lower bounds of the ranges (verified by comparison with Table 22).

## 3. TAW, RAW, Dr, p and MAD

### Takeaway
TAW is the bucket's full usable size; Dr (depletion) is how much is missing from full (field capacity); RAW = p x TAW is the part of the bucket the crop can drain without stress. Stress begins only after Dr exceeds RAW, so irrigation is aimed at the RAW point, not the wilting point.

### Cited Findings
- TAW: water between FC and WP in the root zone, mm (Eq. 82) — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- RAW = p x TAW (Eq. 83): the portion of TAW a crop can extract before stress begins — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- p: the average fraction of TAW that can be depleted from the root zone before moisture stress (reduction in ET) occurs — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Dr (root-zone depletion): shortfall of root-zone water relative to field capacity; zero at FC; stress begins when Dr exceeds RAW. Dr is bounded 0 <= Dr <= TAW (Eq. 86) — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Initial depletion from a measured water content: Dr = 1000 (thetaFC - theta) Zr (Eq. 87); after heavy rain or irrigation Dr can be assumed near zero — [FAO-56 Ch. 8, Eq. 87](http://www.fao.org/4/x0490E/x0490e0e.htm)
- MAD (management allowed depletion): similar to RAW but also shaped by management and economic factors. MAD is lower than RAW under risk aversion or uncertainty, and higher when controlled stress is deliberate — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Once Dr exceeds RAW, crop ET "begins to decrease in proportion to the amount of water remaining in the root zone" — [FAO-56 Ch. 8, text introducing Fig. 42](http://www.fao.org/4/x0490E/x0490e0e.htm)
- To avoid stress, irrigations should be applied before or at the moment the readily available water is depleted — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- p normally varies from about 0.30 for shallow-rooted plants at high ETc to about 0.70 for deep-rooted plants at low ETc; Table 22 values run from 0.20 (e.g. celery, spinach) to 0.80 (sisal); "a value of 0.50 for p is commonly used for many crops" — [FAO-56 Ch. 8, Table 22 text](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Level versus depletion: level in the bucket = TAW - Dr (project's framing, implied by Eq. 82-86; the project works with the level, FAO with depletion). Stress threshold in level terms = TAW - RAW = (1 - p) TAW.

### Inferences
- Physical meaning (my reading, not FAO wording): as soil dries, the remaining water is held more tightly, so roots must work harder; early on plants take water freely, and only after RAW is gone does uptake lag demand and the plant close stomata. That is why "empty" (wilting point) is not the irrigation target. Also water is not used uniformly: the wettest part of the root zone is not perfectly accessible, so a safety margin helps.
- Depletion in the plain bucket picture: Dr = empty space at the top; level = water that is left.
- MAD vs the project's half rule: in the project, the "half" threshold plays the role of MAD (a manager's choice), not RAW (a crop property). Project notes state MAD = p in Annex 8 (so there it equals RAW), but that is not used in the plan.

### Gaps
- FAO's wording on why the plant is stressed after RAW (physiology) is not in the passages I fetched beyond "ET reduces in proportion"; the physiological explanation above is an inference.

## 4. FAO p values (tomato 0.40, bell pepper 0.30), ETc adjustment, and the "irrigate at 50%" rule

### Takeaway
FAO's Table 22 allows tomato to lose 40% of TAW and bell pepper 30% before stress (at ETc about 5 mm/d), lower still on hot days. The project's rule irrigates when the level would fall below half the bucket, i.e. allows 50% depletion: this is a simplification chosen by the project, NOT an FAO value, and for both crops it is looser (later) than FAO's no-stress threshold.

### Cited Findings
- Table 22: tomato p = 0.40, sweet pepper (bell) p = 0.30 — [FAO-56 Ch. 8, Table 22](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Table 22 footnote 2: p values apply for ETc about 5 mm/day; p can be adjusted for other ETc rates; p is higher at low ETc and lower in hot, dry weather — [FAO-56 Ch. 8, Table 22 footnote 2](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Adjustment: p = p(Table 22) + 0.04 (5 - ETc), ETc in mm/day, limited to 0.1 <= p <= 0.8 — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm) (I got this from the fetched text, not the image; the project notes carry the same formula)
- "A value of 0.50 for p is commonly used for many crops" — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Project rule: irrigate when the level would fall below 0.5 x TAW, for both crops, "task spec"; no Ks and no p adjustment; exactly half does not trigger. Source of the 0.5 in the project is the task specification, not FAO — [SKILL.md](/home/nereya/AgroPilot/.claude/skills/irrigation-calc-reference/SKILL.md), [irrigation.py bucket_day](/home/nereya/AgroPilot/services/planner-service/irrigation.py)

### Inferences (calculations from the formula above)
- Adjusted p examples: tomato at ETc 3 mm/d p = 0.48; at 5 -> 0.40; at 7 -> 0.32. Bell pepper at 3 -> 0.38; at 5 -> 0.30; at 7 -> 0.22.
- In level terms (FAO's no-stress point = level of (1 - p) TAW): tomato at ETc 5, irrigate when level is at or below 60% of TAW; bell pepper, at or below 70%. The project's rule waits until the level is below 50%, so, relative to FAO's p, the project rule lets both crops go past the point where FAO says stress starts (10 percentage points of TAW for tomato, 20 for bell pepper at ETc 5 mm/d, and more on hotter days). So the half rule is not "safe" by FAO's numbers: it accepts some mild water stress, most for bell pepper. The 0.5 figure matches FAO's generic "commonly used 0.50" remark, but FAO does not give 0.5 for these crops.
- Algebra: p adjusted would equal 0.5 for tomato only at ETc = 2.5 mm/d (0.40 + 0.04 x 2.5), and for bell pepper only at ETc = 0 (not reachable).
- The half rule ignores crop differences, ETc level and stress; it is simple and uniform. Whether acceptable depends on the project's tolerance for stress (a project decision I could not verify).
- Ks note: the project's plan does not apply Ks, so mild stress is not reduced from the calculated ETc; the plan assumes the crop uses full ETc even below the RAW point.

### Gaps
- The project's reasons for choosing 0.5 beyond "task spec" are not documented in the files I read.
- The 0.5 trigger in the project refers to level being below half; FAO's p refers to depletion exceeding RAW; I mapped between them with level = TAW - Dr.

## 5. The stress coefficient Ks

### Takeaway
Ks is a 0-1 multiplier on crop water use. It is 1 while depletion is within RAW, then falls linearly to 0 as the bucket drains to empty.

### Cited Findings
- Eq. 84 (read visually from the equation image): Ks = (TAW - Dr) / (TAW - RAW) = (TAW - Dr) / ((1 - p) TAW), for Dr > RAW — [FAO-56 Ch. 8, Eq. 84 image](http://www.fao.org/4/x0490E/x0490e2w.gif)
- Ks = 1 when Dr <= RAW; Ks is a dimensionless transpiration reduction factor from 0 to 1 — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Stressed ETc: ETc adj = Ks x Kc x ETo (Eq. 81, single Kc); Eq. 80 with dual Kc: ETc adj = (Ks Kcb + Ke) ETo — [project notes fao56.md sec. 1](/home/nereya/AgroPilot/services/planner-service/docs/research/fao56.md) (secondhand; I did not re-fetch Ch. 8 for Eqs. 80/81)

### Inferences
- Worked example: TAW 70, p 0.4, RAW 28, Dr 42: Ks = (70 - 42)/(70 - 28) = 28/42 = 0.667; the crop uses about two thirds of its normal water. At Dr = 70 (empty) Ks = 0; at Dr = 28 Ks = 1 (check: (70-28)/42 = 1).
- The formula is a straight line, so each mm of extra depletion beyond RAW cuts use by the same fraction; this is FAO's model, an approximation of real crops.

### Gaps
- Whether Dr in Ks is start-of-day or end-of-day: the source does not say (project notes; the project uses start-of-day).

## 6. The daily water balance

### Takeaway
Each day: rain, irrigation and capillary rise refill the bucket; crop use (ETc) and deep percolation drain it. FAO tracks depletion (Eq. 85); the project tracks the level. Anything above full drains away.

### Cited Findings
- Eq. 85: Dr,i = Dr,i-1 - (P - RO)i - Ii - CRi + ETc,i + DPi (mm; end-of-day depletion on day i). P = precipitation, RO = runoff, I = net irrigation depth infiltrating, CR = capillary rise from the water table, ETc = crop evapotranspiration, DP = deep percolation — [FAO-56 Ch. 8, Eq. 85](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Rain, irrigation and capillary rise reduce depletion; ETc and deep percolation increase it (as written; see inference on DP) — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Eq. 86: 0 <= Dr <= TAW — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Eq. 88: DPi = (Pi - ROi) + Ii - ETc,i - Dr,i-1, and DP is never negative (it applies when this exceeds zero after heavy wetting) — [FAO-56 Ch. 8, Eq. 88](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Water above field capacity is assumed lost the same day by deep percolation — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Runoff is estimated with standard hydrological methods; FAO does not give a simple rule in Ch. 8 — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Capillary rise depends on soil type, water-table depth and root-zone wetness; it can usually be taken as zero if the water table is more than about 1 m below the root zone — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- A rain threshold: project notes say P below about 0.2 ETo is usually ignored (secondhand from Ch. 8 Eq. 85 text) — [project notes fao56.md sec. 1](/home/nereya/AgroPilot/services/planner-service/docs/research/fao56.md); not re-verified by me.
- Project (level form): L_pre = min(TAW, L_prev + rain - ETc); if L_pre < 0.5 TAW then need = TAW - L_pre (refill to full) and end level = TAW; else need = 0 and end level = L_pre. Runoff, capillary rise and ignoring small rain are not applied; bucket full at day 1 — [SKILL.md](/home/nereya/AgroPilot/.claude/skills/irrigation-calc-reference/SKILL.md), [irrigation.py bucket_day](/home/nereya/AgroPilot/services/planner-service/irrigation.py)

### Inferences
- Level and depletion are two views of one quantity: level = TAW - Dr. Rain adds to level; ETc subtracts. In FAO's form DP is shown as a positive term in Eq. 85 but, per Eq. 86-88, depletion is floored at 0 (full bucket): the excess cannot be stored, it drains. In the project's `min(TAW, ...)` the cap does the same job.
- When rain exceeds the empty space: example, bucket 70 mm, level 55 mm (15 mm empty), ETc 5, rain 30: raw sum 55 + 30 - 5 = 80, cap at 70, so 10 mm is lost to deep percolation. FAO Eq. 88 check: DP = 30 + 0 - 5 - 15 = 10 mm. Both agree.
- Rain a farmer sees on a gauge may not all count: part may run off (RO) on slopes or hard soil, which the project ignores.

### Gaps
- Eq. 85 itself was read as text from the fetch, not from its image; the project notes agree.
- Runoff method not in FAO Ch. 8; the project assumes zero.

## 7. Numeric walkthrough: 70 mm bucket, 7 mm/day, irrigate at half

Setup (illustrative, mine): bucket TAW = 70 mm (for example 100 mm/m x 0.7 m), starting full, ETc = 7 mm/day, no rain, no irrigation; trigger = 0.5 x 70 = 35 mm; irrigate when level would fall below 35 (exactly 35 does not trigger, per irrigation.py). Using the project's rule from [SKILL.md](/home/nereya/AgroPilot/.claude/skills/irrigation-calc-reference/SKILL.md) and [irrigation.py](/home/nereya/AgroPilot/services/planner-service/irrigation.py).

| Day | Start level (mm) | Crop use (mm) | Level after use (mm) | Compare with 35 | Action |
|---|---|---|---|---|---|
| 1 | 70 | 7 | 63 | above | none |
| 2 | 63 | 7 | 56 | above | none |
| 3 | 56 | 7 | 49 | above | none |
| 4 | 49 | 7 | 42 | above | none |
| 5 | 42 | 7 | 35 | exactly half, not below | none |
| 6 | 35 | 7 | 28 (would be) | below 35 | irrigate |

- Day 6: need = TAW - L_pre = 70 - 28 = 42 mm, end level back to 70 (project's refill-to-full rule).
- Same in depletion terms: Dr after day 5 = 35 = 0.5 TAW; day 6 would give Dr = 42 (60% of TAW).
- FAO comparison with p = 0.4 at this ETc: ETc 7 mm/d gives p = 0.40 + 0.04(5 - 7) = 0.32 (tomato); RAW = 0.32 x 70 = 22.4 mm; stress starts when Dr > 22.4, i.e. level < 47.6 mm, which happens on day 4 (level 42, Dr 28 > 22.4). So at ETc 7 mm/d, FAO's no-stress limit is passed during day 4, before the project's half rule triggers. Ks for the start of day 5 using Dr = 28: (70 - 28)/(70 - 22.4) = 0.882. This shows the half rule would let the crop run somewhat stressed under hot demand (illustrative; my calculation, with the p adjustment applied to the tomato value).
- Annex 8 irrigates when end-of-day depletion exceeds RAW (project notes), so FAO's approach would irrigate earlier than the project rule here.

### Gaps
- None for the arithmetic (I recomputed the table). The use of 7 mm/day is a teaching number: it is a high but possible daily ETc, and equals the lead's requested example.

## 8. Why yesterday's rain still counts today

### Takeaway
Soil stores water. Rain that soaks into the root zone stays there (up to field capacity) and is used over the following days, so the bucket level carries forward from day to day.

### Cited Findings
- The balance is a running account: today's depletion is built from yesterday's, Dr,i = Dr,i-1 + ... — [FAO-56 Ch. 8, Eq. 85](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Water up to field capacity is retained against gravity; only water above field capacity is lost the same day — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- Project: L_pre = min(TAW, L_prev + rain - ETc), L_prev carrying yesterday's end level — [irrigation.py](/home/nereya/AgroPilot/services/planner-service/irrigation.py)

### Inferences
- Example: level 40 mm entering a day, 12 mm rain, ETc 5.75: 40 + 12 - 5.75 = 46.25 mm (the skill's case 5), so no irrigation; tomorrow starts from 46.25, not from where it would have been without rain. Rain only "helps" until the bucket is full; more than that is wasted.
- Contrast: skipping yesterday's rain would trigger irrigation too early and waste water.

### Gaps
- Real soils also lose some rain to surface runoff, and a heavy rain can exceed what the soil can soak in; neither is in the project's calculation.

## 9. Common misunderstandings

### Takeaway
Most confusion comes from treating the bucket as "empty at zero", from thinking half is an FAO number, and from forgetting that overflow is lost.

### Cited Findings
- "Plants can use all the water down to wilting point without harm": no, FAO says ET starts to fall once Dr exceeds RAW; the usable-without-stress part is only p x TAW — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- "Half (50%) is FAO's rule": no, FAO says p = 0.40 for tomato and 0.30 for bell pepper (at ETc about 5 mm/d), and that 0.50 is commonly used for many crops; the project's half rule is its own simplification — [FAO-56 Ch. 8, Table 22](http://www.fao.org/4/x0490E/x0490e0e.htm), [SKILL.md](/home/nereya/AgroPilot/.claude/skills/irrigation-calc-reference/SKILL.md)
- "More rain always helps": water above field capacity drains away the same day — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)
- "p is fixed": it changes with ETc (hot dry weather lowers p) — [FAO-56 Ch. 8, Table 22 fn 2 and p adjustment](http://www.fao.org/4/x0490E/x0490e0e.htm)
- "Root depth = maximum": FAO says smaller Zr suit scheduling — [Table 22 fn 1](http://www.fao.org/4/x0490E/x0490e0e.htm)
- "TAW is a property of the crop": it depends on both soil (theta difference) and root depth (Eq. 82); p depends on the crop and weather (Table 22) — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm)

### Inferences
- "Dry surface means dry bucket": the surface layer dries first; the bucket model uses the whole root zone average, so a dry surface does not on its own mean irrigation is due (my inference; FAO's single-Kc bucket does not model layers).
- "The same mm of water means the same in every soil": 35 mm is half of a 70 mm bucket but is a different share of a sand bucket (58 mm) or clay-loam (140 mm); the same trigger fraction means different mm and different frequencies.
- Soil type changes how often you irrigate: a small bucket (sand, shallow roots) empties to half in few days, so irrigations are small and frequent (project values: sand/tomato 58.1 mm bucket gives a 29.05 mm trigger).
- Mismatch to note for the plain-language step: FAO's p is "depletion allowed", the project's 0.5 is "level allowed to fall to". For a 0.5 rule these are the same number, but for p = 0.4 the level limit is 0.6. Be careful not to mix them.

### Gaps
- None beyond those flagged above; no source found for typical irrigation frequency claims, so none are made beyond the arithmetic.
