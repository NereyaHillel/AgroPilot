# FAO-56 research notes for the planner

Date: 2026-11-15 (date accessed). Source: FAO Irrigation and Drainage Paper 56 (Allen et al., 1998), HTML edition at http://www.fao.org/4/x0490E/ (the www.fao.org/3/ URL 301-redirects there).
Scope: Chapter 5, Chapter 6, Chapter 8, Annex 8, plus Tables 11, 12, 19, 20, 22 wherever they live. Written for a daily drip-irrigation planner (tomato, bell pepper).

## Reading method and limits (read first)

- Every page was read through the WebFetch tool, which returns a model-made summary, not raw text. Equations in the FAO HTML are mostly images, so many could not be read. Where an equation form was not readable it is marked **NOT READABLE**; nothing was filled from memory.
- Equations marked "reconstructed" were recovered by the fetch tool from worked examples, not from the equation image. Verify them against the PDF/printed paper before coding.
- "Inference:" marks my own reasoning, not source text.
- TOC check: Ch. 5 = "Introduction to crop evapotranspiration (ETc)", Ch. 6 = "ETc - Single crop coefficient (Kc)", Ch. 8 = "ETc under soil water stress conditions". **Annex 8 = "Calculation example for applying the dual Kc procedure in irrigation scheduling"**, so it uses Kcb + Ke, not the single Kc (TOC, x0490e00.htm).

## 1. From ET0 and Kc to crop water need

Source: Ch. 5 http://www.fao.org/4/x0490E/x0490e0a.htm; Ch. 6 x0490e0b.htm; Ch. 8 x0490e0e.htm.

- **Eq. 56** (Ch. 5): ETc = Kc x ETo (mm/d). ETc is crop ET under standard conditions (large fields, excellent agronomic and soil water conditions, no water stress). ETo is FAO Penman-Monteith ETo. Kc is dimensionless. (Ch. 5)
- **Eq. 58** (Ch. 6): the same relation, ETc = Kc x ETo, restated as the single-Kc procedure (Ch. 6). Note the number differs from Ch. 5 (56).
- **Eq. 57** (Ch. 5): Kc = Kcb + Ke (dual approach: basal coefficient + soil evaporation coefficient). Ch. 5 says single Kc suits weekly or longer periods, planning, and surface/set-sprinkler irrigation; the dual approach suits daily real-time scheduling and high-frequency irrigation. Ch. 5 says Kc from Eq. 56 is the upper limit of ETc; stress or poor conditions are handled as ETc adj (Ch. 8).
- Ch. 6 procedure: (1) identify stages and lengths, (2) adjust Kc for wetting frequency and climate, (3) build the Kc curve, (4) ETc = Kc x ETo.
- **Stressed ETc** (Ch. 8): Eq. 80: ETc adj = (Ks Kcb + Ke) ETo. Eq. 81: ETc adj = Ks Kc ETo. Ch. 8 calls Eq. 80 "generally more valid" because Ks affects only transpiration, and Eq. 81 reasonable when soil evaporation is a small share of ETc.
- **Net irrigation requirement.** The source has no stand-alone equation named "irrigation requirement" in the scope read. It is implicit in the root-zone balance, **Eq. 85** (section 3 below): I (net irrigation, mm) is the term that returns depletion toward 0, and P - RO is effective rain. Ch. 8 text: P below about 0.2 ETo is usually ignored (Ch. 8, Eq. 85 definitions). Inference: with CR = 0, DP = 0 and RO = 0, net need over a period = ETc adj - P_effective - change in stored water.
- **Climate premise:** Kc tables assume sub-humid climate, RHmin about 45%, u2 about 2 m/s (Ch. 5 "Climate"; Table 12 notes).

## 2. Kc and growth stages for tomato and bell pepper

### 2.1 Stage lengths, Table 11 (Ch. 6, x0490e0b.htm, section "Vegetables - Solanum Family")

Days; footnote: lengths "are indicative of general conditions, but may vary substantially from region to region". No row-specific footnotes. Ch. 6 says to prefer local observations.

| Crop | Init | Dev | Mid | Late | Total | Plant date | Region |
|---|---|---|---|---|---|---|---|
| Tomato | 30 | 40 | 40 | 25 | 135 | January | Arid region |
| Tomato | 35 | 40 | 50 | 30 | 155 | Apr/May | California, USA |
| Tomato | 25 | 40 | 60 | 30 | 155 | Jan | California desert, USA |
| Tomato | 35 | 45 | 70 | 30 | 180 | Oct/Nov | Arid region |
| Tomato | 30 | 40 | 45 | 30 | 145 | Apr/May | Mediterranean |
| Sweet pepper (bell) | 25/30 | 35 | 40 | 20 | 125 | Apr/Jun | Europe and Mediterranean |
| Sweet pepper (bell) | 30 | 40 | 110 | 30 | 210 | October | Arid region |

Ambiguity: the pepper "25/30" initial length is printed as two values with no explanation in what I read; the planner must choose (or let the user override). Ch. 5 defines stages: initial = planting to about 10% ground cover; development = to effective full cover (flowering, or LAI about 3); mid = to start of maturity/senescence; late = to harvest. Kc ini depends on wetting frequency and ETo; Kc mid is the maximum.

### 2.2 Kc values, Table 12 (Ch. 6, x0490e0b.htm, Solanum family)

| Crop | Kc ini | Kc mid | Kc end | Max height h (m) | Footnote |
|---|---|---|---|---|---|
| Solanum family group row | 0.6 | 1.15 | 0.80 | not shown | none |
| Tomato | no separate value read | 1.15 | 0.70-0.90 | 0.6 | 2 |
| Sweet pepper (bell) | no separate value read | 1.05 | 0.90 | 0.7 | 2 |

- Kc ini: the per-crop Kc ini cell for tomato is **blank in the source HTML** (checked in the raw table markup, 2026-11-15); only the Solanum group row carries 0.6. Inference: 0.6 applies to both crops. The sweet pepper row was not re-checked in raw markup.
- Tomato Kc end is a range (0.70-0.90) with no rule in what I read for choosing within it. The planner must choose (and expose it).
- Footnote 1 (Kc ini): approximate, for typical irrigation; frequent wetting (high-frequency sprinkler, daily rain) can raise Kc ini toward 1.0-1.2; refine with Figs. 29/30, Eq. 7-3 in Annex 7, or the dual approach.
- Footnote 2: peppers and tomatoes are sometimes staked to 1.5-2 m. Then Kc mid may be 1.15 for peppers and 1.20 for tomatoes, and h should be increased.
- Table notes: time-averaged single Kc for non-stressed, well-managed crops, sub-humid climate (RHmin about 45%, u2 about 2 m/s), for use with FAO-PM ETo. Kc mid adjustable by Eq. 62, Kc end by Eq. 65 (only if tabulated Kc end is at least 0.45).

### 2.3 Climate adjustments (Ch. 6)

- **Eq. 62** (Kc mid adjustment for u2, RHmin, h): **VERIFIED from the equation image** (x0490e2d.gif, 2026-11-15): Kc mid = Kc mid(Tab) + [0.04 (u2 - 2) - 0.004 (RHmin - 45)] (h/3)^0.3. u2 = mean daily wind speed at 2 m during mid-season (m/s), 1 <= u2 <= 6; RHmin = mean daily minimum relative humidity during mid-season (%), 20 <= RHmin <= 80; h = mean plant height during mid-season (m), 0.1 < h < 10 (Ch. 6). Eqs. 63-64 estimate RHmin from dewpoint or Tmin. Figure 32, Tables 15-16 give additive adjustments and general wind/humidity classes.
- **Eq. 65** (Kc end adjustment): **VERIFIED from the equation image** (x0490e2i.gif): same form as Eq. 62 with Kc end(Tab) in place of Kc mid(Tab): Kc end = Kc end(Tab) + [0.04 (u2 - 2) - 0.004 (RHmin - 45)] (h/3)^0.3, same variable ranges. Applies only when tabulated Kc end >= 0.45 (the table note and text word the threshold slightly differently); u2, RHmin and h are values for the late-season stage per Ch. 6 (not re-read here). Tomato Kc end 0.70-0.90 and pepper 0.90 are above the threshold.

### 2.4 Kc ini and drip / partial wetting (Ch. 6)

- Kc ini depends on wetting interval, ETo, and wetting depth (range about 0.1 to 1.15). Fig. 29 is for light wetting (about 10 mm or less per event), Fig. 30 (30a coarse, 30b fine/medium soils) for heavy wetting (40 mm or more). **Eq. 59** interpolates for average infiltration depth 10-40 mm; **VERIFIED from the equation image** (x0490e2b.gif): Kc ini = Kc ini(Fig 29) + [(I - 10)/(40 - 10)] x (Kc ini(Fig 30) - Kc ini(Fig 29)). Table 13 classes rain depths.
- **Eq. 60**: Kc ini = fw x Kc ini(Table/Figure), fw = fraction of surface wetted. **Eq. 61**: Iw = I / fw (depth over the wetted part, used to choose Fig. 29 vs 30; per Example 26).
- Example 26 (trickle): fw about 0.4, interpolated 1.05, giving Kc ini = 0.42. With mixed rain and irrigation, fw is an infiltration-depth-weighted average.
- **Table 20** (Ch. 7, x0490e0c.htm): fw for trickle irrigation 0.3...0.4; precipitation, sprinkler, basin, border 1.0; furrow every furrow narrow bed 0.6...1.0, wide bed 0.4...0.6; alternate furrows 0.3...0.5.
- Inference: under drip, Eq. 60 lowers Kc ini roughly in proportion to fw; the source does not say whether Kc mid or Kc end are scaled by fw (Ch. 6 as read gives fw only for Kc ini). Whether to scale Kc mid/end for drip is a planner decision, not supported here.
- Inference: using Table 12's 0.6 for Kc ini times fw 0.3-0.4 gives 0.18-0.24; the source gives the 0.42 example only for a Fig.-derived 1.05. Applying Eq. 60 to the 0.6 table value is a choice (Eq. 60 text says "Tab/Fig").

### 2.5 Building the Kc curve (Ch. 6, Figs. 34-36, Eq. 66)

1. Split the season into four stages with lengths (Table 11 or local). 2. Take Kc ini, Kc mid, Kc end (Table 12) and adjust (Eqs. 60, 62, 65). 3. Draw straight segments: Kc ini flat through the initial stage, Kc mid flat through mid-season, linear across development (ini to mid) and late season (mid to end).
- **Eq. 66** (**VERIFIED from the equation image** x0490e2k.gif): Kc_i = Kc_prev + [(i - SUM(L_prev))/L_stage] x (Kc_next - Kc_prev), i = day number of the season, SUM(L_prev) = sum of the lengths of all previous stages, L_stage = length of the stage being interpolated.
- Premature harvest: the curve may be cut at the actual harvest date (Ch. 6). Box 15 / Example 28 apply this to dry beans.
- Ambiguity: the source does not say whether day 1 of the season is planting day or the day after, or how to treat days beyond the summed stage lengths.

## 3. The soil water bucket (Ch. 8, http://www.fao.org/4/x0490E/x0490e0e.htm)

- **Eq. 82**: TAW = 1000 (thetaFC - thetaWP) Zr, TAW in mm, theta in m3/m3, Zr (rooting depth) in m. thetaFC is water held after drainage largely ceases; thetaWP is the content at which uptake stops.
- **Eq. 83**: RAW = p x TAW.
- p: fraction of TAW that can be depleted before ET is reduced. Adjusting p for ETc (Ch. 8): p = p(Table 22) + 0.04 (5 - ETc), ETc in mm/d, limited to 0.1 <= p <= 0.8. Table 22 values are for ETc about 5 mm/d.
- **Eq. 84** (Ks when Dr > RAW): **VERIFIED from the equation image** (x0490e2w.gif): Ks = (TAW - Dr)/(TAW - RAW) = (TAW - Dr)/((1 - p) TAW). Ks = 1 when Dr <= RAW (Ch. 8). Ks is a dimensionless 0-1 transpiration reduction factor. The source does not say whether Dr here is the start-of-day (Dr,i-1) or end-of-day value; that is an implementer choice.
- **Eq. 85**: Dr,i = Dr,i-1 - (P_i - RO_i) - I_i - CR_i + ETc,i + DP_i (all mm; depletion at end of day i). P = precipitation; RO = runoff (by "standard procedures from hydrological texts"); I = net irrigation infiltrating (field average); CR = capillary rise (assumed 0 if the water table is more than about 1 m below the root zone); DP = deep percolation. **Eq. 86**: 0 <= Dr,i <= TAW. **Eq. 87**: initial depletion Dr = 1000 (thetaFC - theta) Zr. **Eq. 88**: DP_i = (P_i - RO_i) + I_i - ETc,i - Dr,i-1 >= 0 (excess after wetting beyond field capacity).
- **Kc adj = Ks x Kc**: Eq. 81 above (single Kc) or Eq. 80 (dual). The Ch. 8 page as read says nothing about drip or partial wetting; Ks under saline conditions should be used only with the dual approach.
- Root depth over the season: no general growth curve in Ch. 8. Example 38 assumes Zr rising from 0.30 m (day 1) to 0.35 m (day 10), adding subsoil water at field capacity as roots deepen: Dr,i = Dr,i-1 + 1000 (thetaFC - theta_sub) delta-Zr. Annex 8 grows Zr in proportion to Kcb (section 4).
- **Table 22** (Ch. 8): tomato Zr max 0.7-1.5 m, p 0.40; sweet pepper (bell) Zr max 0.5-1.0 m, p 0.30. No row footnotes. General notes: smaller Zr suits irrigation scheduling, larger Zr modelling/rainfed; p valid at ETc about 5 mm/d. The planner must pick Zr within these ranges (Inference: the smaller end for scheduling per the general note).
- **Table 19** (Ch. 7, x0490e0c.htm), thetaFC / thetaWP (m3/m3), ranges: sand 0.07-0.17 / 0.02-0.07; loamy sand 0.11-0.19 / 0.03-0.10; sandy loam 0.18-0.28 / 0.06-0.16; loam 0.20-0.30 / 0.07-0.17; silt loam 0.22-0.36 / 0.09-0.21; silt 0.28-0.36 / 0.12-0.22; silty clay loam 0.30-0.37 / 0.17-0.24; silty clay 0.30-0.42 (printed "0-30") / 0.17-0.29; clay 0.32-0.40 / 0.20-0.24. Differences (thetaFC - thetaWP): sand 0.05-0.11, loamy sand 0.06-0.12, sandy loam 0.11-0.15, loam 0.13-0.18, silt loam 0.13-0.19, silt 0.16-0.20, silty clay loam 0.13-0.18, silty clay 0.13-0.19, clay 0.12-0.20. Table 19 also lists evaporation REW/TEW (not needed for the single-Kc bucket).
- Ch. 8 Example 36 values (illustrative): loamy sand 0.15/0.06 (90 mm/m), silt 0.32/0.15 (170 mm/m), silty clay 0.35/0.23 (120 mm/m).
- Not in scope read: Ky and salinity (Eqs. 89-93, Tables 23-24) exist but were not needed.

## 4. Annex 8: day-by-day scheduling (http://www.fao.org/4/x0490E/x0490e0p.htm)

Caveat: Annex 8 is a spreadsheet example for dry beans (Kimberly, 1974) with the **dual** Kc. Its Box 8.1 formulas are images/cell references; the summary I read is paraphrased and equation numbers there may be mis-mapped. Treat this section as structure, not as formula source.

- **Structure:** Figure 8.1 (spreadsheet, three image pages), Box 8.1 (cell formulas, footnotes 1-12), Table 8.1 (extra variable names), Figure 8.2 (daily Kcb/Kc), Figure 8.3 (end-of-day depletion). The schedule is theoretical and differs from the actual one in Ch. 7 Box 16.
- **Inputs:** planting 22 May; stages 25/25/30/20 d; Kcb ini 0.15, mid 1.1, end 0.25; max height 0.4 m; TEW 22 mm, REW 8 mm, initial De 18 mm (derivation not explained); available water 160 mm/m; Rootmin 0.2 m, Rootmax 0.8 m (Zr min typically 0.15-0.20 m); fw irrigation 0.5, initial fw 1; MAD 70% in the initial stage, 45% afterwards, with p = MAD; daily ETo, Tmax, u2, Tdew (RHmin derived).
- **Daily steps (order as summarized):** day of year; RHmin; Kcb from stage (linear in development/late; mid/end adjusted for wind and humidity); crop height (non-decreasing, proportional to Kcb); Kc max; Zr proportional to Kcb (non-decreasing); fw; evaporation-layer depletion and stage factors; Ke (limited by Kc max and energy); Kc = Kcb + Ke and ETc = Kc ETo; root-zone depletion first estimated by Eq. 85 with zero drainage and unstressed ETc; Ks (Eq. 80) when depletion exceeds RAW, stress point = MAD; depletion recomputed after drainage and stress, recorded as end-of-day depletion.
- **Allowable depletion:** MAD/100 x Zr x available water (the annex does not use the term TAW; it equals RAW when p = MAD).
- **Trigger:** irrigation is scheduled for the next morning if end-of-day depletion exceeds RAW, within the growing period and before the middle of the late season (footnote 10); last irrigation day 225. First-day irrigation is zero (footnote 4).
- **Amount:** net depth equals the previous day's end-of-day depletion, i.e. refills to field capacity; the applied depth is divided by fw to express it over the wetted fraction (footnote 4). Some stress can occur on the day before irrigation because irrigation waits until depletion reaches RAW (effect on Kc adj said to be small).
- **Timing assumption:** irrigation and rain occur early in the morning, so they reduce start-of-day depletion.
- **Rain/runoff/DP:** runoff assumed zero (add hydrology-text methods if needed); excess precipitation drains the same day; no rain threshold given.
- **Outputs:** total irrigation depth, number of irrigations and dates are not stated in the text read (only in the figures).

## 5. Choices and gaps for the implementer

1. Equations 59, 62, 65, 66 and 84 were read from the FAO equation images after the first pass (see section 2.3-2.5 and 3). Eq. 63-64 and Annex 8 Box 8.1 formulas remain unread.
2. Per-crop Kc ini for tomato and pepper is blank in Table 12; only the Solanum group 0.6 exists. Footnote 1 warns it rises with frequent wetting.
3. Tomato Kc end is a range; pepper stage 1 length "25/30"; several Table 11 variants (region/planting date) need a selection rule.
4. Drip: the source only scales Kc ini by fw (Eq. 60; Table 20 trickle 0.3-0.4). Whether Kc mid/end or Zr change under drip is not covered in what was read.
5. Single Kc (Ch. 6/8, Eq. 81) versus dual Kc (Annex 8): the Annex 8 daily procedure needs Ke and evaporation-layer data; a single-Kc planner must simplify. Ch. 5 says single Kc is best for weekly or longer periods and daily use is better served by dual Kc.
6. Zr and p choices within Table 22 ranges; p varying with ETc (limits 0.1-0.8); no season-long Zr growth rule in Ch. 8.
7. Units and rounding: all depths mm, ETo mm/d, Zr m; the source specifies no rounding. Rain below about 0.2 ETo ignored (Ch. 8); no effective-rain formula beyond P - RO.
8. Annex 8 irrigates the whole previous-day depletion, one trigger rule; the source does not cover deficit irrigation, irrigation intervals or system capacity.

## Sources

- TOC: http://www.fao.org/4/x0490E/x0490e00.htm (redirect from https://www.fao.org/3/x0490E/x0490e00.htm)
- Chapter 5: http://www.fao.org/4/x0490E/x0490e0a.htm
- Chapter 6 (Tables 11, 12, Eqs. 58-66): http://www.fao.org/4/x0490E/x0490e0b.htm
- Chapter 7 (Tables 19, 20 only): http://www.fao.org/4/x0490E/x0490e0c.htm
- Chapter 8 (Eqs. 80-88, Table 22): http://www.fao.org/4/x0490E/x0490e0e.htm
- Annex 8: http://www.fao.org/4/x0490E/x0490e0p.htm
