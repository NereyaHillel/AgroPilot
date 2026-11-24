# FAO-56 research notes for the planner

Date: 2026-11-15 (date accessed); re-verified 2026-11-24. Source: FAO Irrigation and Drainage Paper 56 (Allen et al., 1998), HTML edition at http://www.fao.org/4/x0490E/ (the www.fao.org/3/ URL 301-redirects there).
Scope: Chapter 5, Chapter 6, Chapter 8, Annex 8, plus Tables 11, 12, 19, 20, 22 wherever they live. Written for a daily drip-irrigation planner (tomato, bell pepper).

## Reading method and limits (read first)

- First pass (2026-11-15): every page was read through the WebFetch tool, which returns a model-made summary, not raw text. Equations in the FAO HTML are mostly images, so many could not be read. Where an equation form was not readable it is marked **NOT READABLE**; nothing was filled from memory.
- Equations marked "reconstructed" were recovered by the fetch tool from worked examples, not from the equation image. Verify them against the PDF/printed paper before coding.
- Re-verification (2026-11-24): the five chapter pages and the TOC were downloaded as raw HTML and read directly (table cells, footnotes, Symbol-font inequality signs); equation GIFs were downloaded and read as images. VERIFIED markers dated 2026-11-24 come from that raw reading.
- "Inference:" marks my own reasoning, not source text.
- TOC check: Ch. 5 = "Introduction to crop evapotranspiration (ETc)", Ch. 6 = "ETc - Single crop coefficient (Kc)", Ch. 8 = "ETc under soil water stress conditions". **Annex 8 = "Calculation example for applying the dual Kc procedure in irrigation scheduling"**, so it uses Kcb + Ke, not the single Kc (TOC, x0490e00.htm).

## 1. From ET0 and Kc to crop water need

Source: Ch. 5 http://www.fao.org/4/x0490E/x0490e0a.htm; Ch. 6 x0490e0b.htm; Ch. 8 x0490e0e.htm.

- **Eq. 56** (Ch. 5): ETc = Kc x ETo (mm/d). ETc is crop ET under standard conditions (large fields, excellent agronomic and soil water conditions, no water stress). ETo is FAO Penman-Monteith ETo. Kc is dimensionless. (Ch. 5)
- **Eq. 58** (Ch. 6): the same relation, ETc = Kc x ETo, restated as the single-Kc procedure (Ch. 6). Note the number differs from Ch. 5 (56).
- **Eq. 57** (Ch. 5): Kc = Kcb + Ke (dual approach: basal coefficient + soil evaporation coefficient). Ch. 5 says single Kc suits weekly or longer periods, planning, and surface/set-sprinkler irrigation; the dual approach suits daily real-time scheduling and high-frequency irrigation. Ch. 5 says Kc from Eq. 56 is the upper limit of ETc; stress or poor conditions are handled as ETc adj (Ch. 8).
- Ch. 6 procedure: (1) identify stages and lengths, (2) adjust Kc for wetting frequency and climate, (3) build the Kc curve, (4) ETc = Kc x ETo.
- **Stressed ETc** (Ch. 8): Eq. 80: ETc adj = (Ks Kcb + Ke) ETo. Eq. 81: ETc adj = Ks Kc ETo. Ch. 8 calls Eq. 80 "generally more valid" because Ks affects only transpiration, and Eq. 81 reasonable when soil evaporation is a small share of ETc.
- **Net irrigation requirement.** The source has no stand-alone equation named "irrigation requirement" in the scope read. It is implicit in the root-zone balance, **Eq. 85** (section 3 below): I (net irrigation, mm) is the term that returns depletion toward 0 (Inference: P - RO acts as effective rain; the source does not use that term). Ch. 8 text: P below about 0.2 ETo is usually ignored (Ch. 8, Eq. 85 definitions). Inference: with CR = 0, DP = 0 and RO = 0, net need over a period = ETc adj - P_effective - change in stored water.
- **Climate premise:** Kc tables assume sub-humid climate, RHmin about 45%, u2 about 2 m/s (Ch. 5 "Climate"; Table 12 title).

## 2. Kc and growth stages for tomato and bell pepper

### 2.1 Stage lengths, Table 11 (Ch. 6, x0490e0b.htm, section "Vegetables - Solanum Family")

Days; footnote: lengths "are indicative of general conditions, but may vary substantially from region to region, with climate and cropping conditions, and with crop variety". No row-specific footnotes. All seven rows below VERIFIED cell by cell in raw HTML (2026-11-24). Ch. 6 says to prefer local observations.

| Crop | Init | Dev | Mid | Late | Total | Plant date | Region |
|---|---|---|---|---|---|---|---|
| Tomato | 30 | 40 | 40 | 25 | 135 | January | Arid region |
| Tomato | 35 | 40 | 50 | 30 | 155 | Apr/May | California, USA |
| Tomato | 25 | 40 | 60 | 30 | 155 | Jan | California desert, USA |
| Tomato | 35 | 45 | 70 | 30 | 180 | Oct/Nov | Arid region |
| Tomato | 30 | 40 | 45 | 30 | 145 | Apr/May | Mediterranean |
| Sweet pepper (bell) | 25/30 | 35 | 40 | 20 | 125 | Apr/Jun | Europe and Mediterranean |
| Sweet pepper (bell) | 30 | 40 | 110 | 30 | 210 | October | Arid region |

Ambiguity: the pepper "25/30" initial length is printed as two values in one cell (VERIFIED in raw HTML, 2026-11-24); Ch. 6 gives no explanation for it; the planner must choose (or let the user override). Ch. 5 defines stages: initial = planting to about 10% ground cover; development = to effective full cover (flowering, or LAI about 3); mid = to start of maturity/senescence; late = to harvest. Kc ini depends on wetting frequency and ETo; Kc mid is the maximum.

### 2.2 Kc values, Table 12 (Ch. 6, x0490e0b.htm, Solanum family)

| Crop | Kc ini | Kc mid | Kc end | Max height h (m) | Footnote |
|---|---|---|---|---|---|
| Solanum family group row | 0.6 | 1.15 | 0.80 | not shown | none |
| Tomato | no separate value read | 1.15 | 0.70-0.90 | 0.6 | 2 |
| Sweet pepper (bell) | no separate value read | 1.05 | 0.90 | 0.7 | 2 |

- Kc ini: the per-crop Kc ini cells for tomato and sweet pepper are both **blank in the source HTML** (`<p><br>`; tomato checked 2026-11-15, both VERIFIED 2026-11-24); only the Solanum group row carries 0.6. Ch. 6 text: "For several group types only one value for K_c ini is listed and it is considered to be representative of the whole group for a typical irrigation water management", so 0.6 applies to both crops. Kc mid 1.05 (pepper) / 1.15 (tomato) carry footnote 2; Kc end 0.90 / 0.70-0.90; h 0.7 / 0.6 (VERIFIED raw, 2026-11-24).
- Tomato Kc end is a range (0.70-0.90) with no rule in what I read for choosing within it. The planner must choose (and expose it).
- Footnote 1 (Kc ini): approximate, for typical irrigation; frequent wetting (high-frequency sprinkler, daily rain) can raise Kc ini toward 1.0-1.2; refine with Figs. 29/30, Eq. 7-3 in Annex 7, or the dual approach.
- Footnote 2: peppers and tomatoes are sometimes staked to 1.5-2 m. Then Kc mid may be 1.15 for peppers and 1.20 for tomatoes, and h should be increased.
- Table title: time-averaged single Kc for non-stressed, well-managed crops, sub-humid climate (RHmin about 45%, u2 about 2 m/s), for use with FAO-PM ETo. The Table 12 notes do not mention Eqs. 62/65; the Ch. 6 text after the table says Kc mid and Kc end should be modified for other climates, via Eq. 62 (Kc mid) and Eq. 65 (Kc end, threshold 0.45; see 2.3).

### 2.3 Climate adjustments (Ch. 6)

- **Eq. 62** (Kc mid adjustment for u2, RHmin, h): **VERIFIED from the equation image** (x0490e2d.gif, 2026-11-15): Kc mid = Kc mid(Tab) + [0.04 (u2 - 2) - 0.004 (RHmin - 45)] (h/3)^0.3. u2 = mean daily wind speed at 2 m during mid-season (m/s), 1 <= u2 <= 6; RHmin = mean daily minimum relative humidity during mid-season (%), 20 <= RHmin <= 80; h = mean plant height during mid-season (m), 0.1 < h < 10 (Ch. 6). **Eq. 63** (**VERIFIED from the equation image** x0490e2e.gif, 2026-11-24): RHmin = e°(Tdew)/e°(Tmax) x 100, Tdew = mean dewpoint and Tmax = mean daily maximum temperature during the mid-season stage, "on a daily or average monthly basis". **Eq. 64** (**VERIFIED from the equation image** x0490e2f.gif): RHmin = e°(Tmin)/e°(Tmax) x 100, used where dewpoint data are missing or doubtful; footnote: in arid and semi-arid climates subtract 2 °C from mean Tmin first (Annex 6, Eq. 6-6). Figure 32, Tables 15-16 give additive adjustments and general wind/humidity classes.
- **Eq. 65** (Kc end adjustment): **VERIFIED from the equation image** (x0490e2i.gif): same form as Eq. 62 with Kc end(Tab) in place of Kc mid(Tab): Kc end = Kc end(Tab) + [0.04 (u2 - 2) - 0.004 (RHmin - 45)] (h/3)^0.3. Ranges: 1 <= u2 <= 6, 20 <= RHmin <= 80, and 0.1 <= h <= 10 (inclusive here, unlike the strict 0.1 < h < 10 for Eq. 62); u2, RHmin and h are late-season-stage means (VERIFIED raw, 2026-11-24). Threshold: the Ch. 6 Kc end text itself words it two ways: "only applied when the tabulated values for K_c end exceed 0.45" and "(i.e., K_c end >= 0.45)"; and "No adjustment is made when K_c end (Table) < 0.45". Table 12's notes do not mention it. Tomato Kc end 0.70-0.90 and pepper 0.90 are above the threshold.

### 2.4 Kc ini and drip / partial wetting (Ch. 6)

- Kc ini depends on wetting interval, ETo, and wetting depth (range about 0.1 to 1.15). Fig. 29 is for light wetting (about 10 mm or less per event), Fig. 30 (30a coarse, 30b fine/medium soils) for heavy wetting (40 mm or more). **Eq. 59** interpolates for average infiltration depth 10-40 mm; **VERIFIED from the equation image** (x0490e2b.gif): Kc ini = Kc ini(Fig 29) + [(I - 10)/(40 - 10)] x (Kc ini(Fig 30) - Kc ini(Fig 29)). Table 13 classes rain depths.
- **Eq. 60**: Kc ini = fw x Kc ini(Table/Figure), fw = fraction of surface wetted. **Eq. 61** (**VERIFIED from the equation image** x0490e2c.gif, 2026-11-24): Iw = I / fw (depth over the wetted part, used to choose Fig. 29 vs 30; per Example 26).
- Example 26 (trickle): fw about 0.4, interpolated 1.05, giving Kc ini = 0.42. With mixed rain and irrigation, fw is an infiltration-depth-weighted average.
- **Table 20** (Ch. 7, x0490e0c.htm): fw for trickle irrigation 0.3...0.4; precipitation, sprinkler, basin, border 1.0; furrow every furrow narrow bed 0.6...1.0, wide bed 0.4...0.6; alternate furrows 0.3...0.5.
- Inference: under drip, Eq. 60 lowers Kc ini roughly in proportion to fw; the source does not say whether Kc mid or Kc end are scaled by fw (Ch. 6 as read gives fw only for Kc ini). Whether to scale Kc mid/end for drip is a planner decision, not supported here.
- Inference: using Table 12's 0.6 for Kc ini times fw 0.3-0.4 gives 0.18-0.24; the source gives the 0.42 example only for a Fig.-derived 1.05. The Eq. 60 text explicitly allows it: "the value for K_c ini obtained from Table 12 or from Figures 29 or 30 should be multiplied by the fraction of the surface wetted" (VERIFIED raw, 2026-11-24).

### 2.5 Building the Kc curve (Ch. 6, Figs. 34-36, Eq. 66)

1. Split the season into four stages with lengths (Table 11 or local). 2. Take Kc ini, Kc mid, Kc end (Table 12) and adjust (Eqs. 60, 62, 65). 3. Draw straight segments: Kc ini flat through the initial stage, Kc mid flat through mid-season, linear across development (ini to mid) and late season (mid to end).
- **Eq. 66** (**VERIFIED from the equation image** x0490e2k.gif): Kc_i = Kc_prev + [(i - SUM(L_prev))/L_stage] x (Kc_next - Kc_prev), i = "day number within the growing season [1.. length of the growing season]", SUM(L_prev) = sum of the lengths of all previous stages, L_stage = length of the stage being interpolated.
- Premature harvest: the curve may be cut at the actual harvest date (Ch. 6, Kc end text). Box 15 / Example 28 build the dry-bean Kc curve and apply Eq. 66 (stages 25/25/30/20, Kc 0.15/1.19/0.35); they do not apply premature harvest.
- Ambiguity: Ch. 6 defines i only as [1.. length of the growing season]; it does not say whether day 1 is planting day or the day after, or how to treat days beyond the summed stage lengths. Annex 8 Box 8.1 cell O14 works in day of year: Kcb ini while J < J_dev (= J_plant + L_ini), interpolation (J - J_dev)/L_dev in development, and it returns Kcb ini for J >= J_harv (also before planting; Figure 8.1 starts on 15 May with J_plant 142).

## 3. The soil water bucket (Ch. 8, http://www.fao.org/4/x0490E/x0490e0e.htm)

- **Eq. 82**: TAW = 1000 (thetaFC - thetaWP) Zr, TAW in mm, theta in m3/m3, Zr (rooting depth) in m. thetaFC is water held after drainage largely ceases; thetaWP is the content at which uptake stops.
- **Eq. 83**: RAW = p x TAW.
- p: fraction of TAW that can be depleted before ET is reduced. Adjusting p for ETc (Ch. 8): p = p(Table 22) + 0.04 (5 - ETc), ETc in mm/d, limited to 0.1 <= p <= 0.8. Table 22 values are for ETc about 5 mm/d.
- **Eq. 84** (Ks when Dr > RAW): **VERIFIED from the equation image** (x0490e2w.gif): Ks = (TAW - Dr)/(TAW - RAW) = (TAW - Dr)/((1 - p) TAW). Ks = 1 when Dr <= RAW (Ch. 8). Ks is a dimensionless 0-1 transpiration reduction factor. Eq. 84 itself does not say which Dr to use, but Ch. 8 Example 37 (a full-grown tomato, Zr 0.8 m, p 0.40) computes Ks from "Root zone depletion at the beginning of the day (column 8 of previous day)", and Annex 8 footnote 11 uses depletion "following any irrigation or precipitation earlier in the day" (VERIFIED raw, 2026-11-24).
- **Eq. 85**: Dr,i = Dr,i-1 - (P_i - RO_i) - I_i - CR_i + ETc,i + DP_i (all mm; depletion at end of day i). P = precipitation; RO = runoff (by "standard procedures from hydrological texts"); I = net irrigation infiltrating (field average); CR = capillary rise (assumed 0 if the water table is more than about 1 m below the root zone); DP = deep percolation. **Eq. 86**: 0 <= Dr,i <= TAW. **Eq. 87**: initial depletion Dr,i-1 = 1000 (thetaFC - theta_i-1) Zr, theta_i-1 = average soil water content of the effective root zone; after heavy rain or irrigation Dr,i-1 about 0. **Eq. 88**: DP_i = (P_i - RO_i) + I_i - ETc,i - Dr,i-1 >= 0 (excess after wetting beyond field capacity).
- **Kc adj = Ks x Kc**: Eq. 81 above (single Kc) or Eq. 80 (dual). The Ch. 8 water-balance text says nothing about drip or partial wetting (trickle irrigation appears only in the salt-toxicity discussion); Ks under saline conditions should be used only with the dual approach.
- Root depth over the season: no general growth curve in Ch. 8. Example 38 assumes Zr rising from 0.30 m (day 1) to 0.35 m (day 10), adding subsoil water at field capacity as roots deepen: Dr,i = Dr,i-1 + 1000 (thetaFC - theta_sub,i-1) delta-Zr (theta_sub assumed at field capacity in the example). Annex 8 grows Zr in proportion to Kcb (section 4, Eq. 8-1).
- **Table 22** (Ch. 8): tomato Zr max 0.7-1.5 m, p 0.40; sweet pepper (bell) Zr max 0.5-1.0 m, p 0.30 (VERIFIED raw, 2026-11-24). No row footnotes. Header footnote 2 repeats p = p(Table 22) + 0.04 (5 - ETc) without the 0.1-0.8 limits; the limits are in the Ch. 8 text. General notes: smaller Zr suits irrigation scheduling, larger Zr modelling/rainfed; p valid at ETc about 5 mm/d. The planner must pick Zr within these ranges (Inference: the smaller end for scheduling per the general note).
- **Table 19** (Ch. 7, x0490e0c.htm), thetaFC / thetaWP (m3/m3), ranges: sand 0.07-0.17 / 0.02-0.07; loamy sand 0.11-0.19 / 0.03-0.10; sandy loam 0.18-0.28 / 0.06-0.16; loam 0.20-0.30 / 0.07-0.17; silt loam 0.22-0.36 / 0.09-0.21; silt 0.28-0.36 / 0.12-0.22; silty clay loam 0.30-0.37 / 0.17-0.24; silty clay 0.30-0.42 (printed "0-30") / 0.17-0.29; clay 0.32-0.40 / 0.20-0.24. Differences (thetaFC - thetaWP): sand 0.05-0.11, loamy sand 0.06-0.12, sandy loam 0.11-0.15, loam 0.13-0.18, silt loam 0.13-0.19, silt 0.16-0.20, silty clay loam 0.13-0.18, silty clay 0.13-0.19, clay 0.12-0.20. Table 19 also lists evaporation REW/TEW (not needed for the single-Kc bucket).
- Ch. 8 Example 36 values (illustrative): loamy sand 0.15/0.06 (90 mm/m), silt 0.32/0.15 (170 mm/m), silty clay 0.35/0.23 (120 mm/m).
- Not in scope read: Ky and salinity (Eqs. 89-93, Tables 23-24) exist but were not needed.

## 4. Annex 8: day-by-day scheduling (http://www.fao.org/4/x0490E/x0490e0p.htm)

Caveat: Annex 8 is a spreadsheet example for dry beans (Kimberly, 1974) with the **dual** Kc. Box 8.1 formulas are HTML text (Excel cell formulas with an "Equation in text" column), read raw 2026-11-24; the Figure 8.1 spreadsheet is three GIFs (x0490e7e/7f/7g.gif). Box 8.1 has typos (e.g. "014" for O14, "16" for I6, "AU 4" for AL14) and footnote 9 says column AK holds end-of-day depletion while the printed AK formula is Ke + Kcb Ks (Eq. 80) and AL is the depletion; treat column letters with care.

- **Structure:** Figure 8.1 (spreadsheet, three image pages), Box 8.1 (cell formulas, footnotes 1-12), Table 8.1 (extra variable names), Figure 8.2 (daily Kcb/Kc), Figure 8.3 (end-of-day depletion). The schedule is theoretical and differs from the actual one in Ch. 7 Box 16.
- **Inputs** (VERIFIED in Box 8.1 and Figure 8.1, 2026-11-24): planting 22 May (month 5, day 22; J_plant 142); stages 25/25/30/20 d; Kcb ini 0.15, mid 1.1, end 0.25; max height 0.4 m; TEW 22 mm, REW 8 mm, initial De 18 mm (derivation not explained); available water 160 mm/m; Rootmin 0.2 m, Rootmax 0.8 m (Zr min typically 0.15-0.20 m); fw irrigation 0.5, initial fw 1; MAD 70% in the initial stage, 45% afterwards, with p = MAD; daily ETo, Tmax, u2, Tdew (RHmin derived by Eq. 63). Kcb mid/end adjusted with Eq. 70 (Ch. 7), giving 1.13 and 0.23 in Figure 8.1.
- **Daily steps (Box 8.1 column order, VERIFIED 2026-11-24):** day of year (D); RHmin (K, Eq. 63); Kcb (O, Eq. 66; linear in development/late); crop height (P, proportional to Kcb, non-decreasing); Kc max (Q, Eq. 72); irrigation / fw (R); fc (S, Eq. 76); fw (T); few (U, Eq. 75); evaporation-layer start depletion (V); Kr (W, Eq. 74); Ke (X, Eq. 71); DPe (Z, Eq. 79); De end (AA, Eq. 77); Kc = Kcb + Ke (AB) and ETc (AC, Eq. 69); Zr (AE, Eq. 8-1, non-decreasing); allowable depletion (AF); root-zone depletion first estimate (AG, Eq. 85, zero drainage, unstressed ETc); net irrigation for next morning (AH); DP (AI, Eq. 88); Ks (AJ, **Eq. 84**, stress point p = MAD); Kc adj = Ke + Ks Kcb (AK, Eq. 80); corrected end-of-day depletion (AL, Eq. 85).
- **Eq. 8-1** (**VERIFIED from the equation image** x0490e5z.gif): Zr,i = Zr min + (Zr max - Zr min) (Kcb,i - Kcb ini)/(Kcb mid - Kcb ini) for J < J_mid; **Eq. 8-2**: Zr,i = Zr max for J >= J_mid. Alternative **Eq. 8-3** (x0490e60.gif): Zr,i = Zr min + (Zr max - Zr min)(J - J_start)/(J_max - J_start) for J_start <= J <= J_max.
- **Allowable depletion:** MAD/100 x Zr x available water (the annex does not use the term TAW; it equals RAW when p = MAD).
- **Trigger:** irrigation is scheduled for the next morning if the first-estimate end-of-day depletion (AG) exceeds the allowable depletion (AF: `IF(AG > AF, AG, 0)`; the text says "greater than or equal to RAW"), from planting until the middle of the late season (footnote 10); last irrigation day 225. First-day irrigation is zero (footnote 4).
- **Amount:** net depth equals the previous day's end-of-day depletion, i.e. refills to field capacity; the applied depth is divided by fw to express it over the wetted fraction (footnote 4). Some stress can occur on the day before irrigation because irrigation waits until depletion reaches RAW ("occasionally causes a small amount of stress on the day prior to irrigation"). The separate statement that the impact of Ks on Kc adj was small refers to before planting and near the end of the season, when Kcb is small.
- **Timing assumption:** irrigation and rain occur early in the morning, so they reduce start-of-day depletion.
- **Rain/runoff/DP:** runoff assumed zero (add hydrology-text methods if needed); excess precipitation drains the same day; no rain threshold given.
- **Outputs:** total irrigation depth, number of irrigations and dates are not stated in the text. The Figure 8.1 GIFs show only rows 14-26 (15-27 May; first net irrigation 25.3 mm decided at the end of 22 May (planting day, J 142), applied on the morning of 23 May as 50.6 mm over fw 0.5). Figure 8.3 (x0490e7i.gif) is a graph only; it shows nine "I" markers between about day 142 and day 225 (read off the graph, approximate).

## 5. Choices and gaps for the implementer

1. Equations 59, 61, 62, 63, 64, 65, 66, 84 and Annex 8 Eqs. 8-1 and 8-3 were read from the FAO equation images; Box 8.1 formulas were read as raw HTML text (2026-11-24).
2. Per-crop Kc ini for tomato and pepper is blank in Table 12; only the Solanum group 0.6 exists. Footnote 1 warns it rises with frequent wetting.
3. Tomato Kc end is a range; pepper stage 1 length "25/30"; several Table 11 variants (region/planting date) need a selection rule.
4. Drip: the source only scales Kc ini by fw (Eq. 60; Table 20 trickle 0.3-0.4). Whether Kc mid/end or Zr change under drip is not covered in what was read.
5. Single Kc (Ch. 6/8, Eq. 81) versus dual Kc (Annex 8): the Annex 8 daily procedure needs Ke and evaporation-layer data; a single-Kc planner must simplify. Ch. 5 says single Kc is used "for weekly or longer time periods, although calculations may proceed on a daily time step" (Table 10 lists daily, 10-day and monthly steps for single Kc); Ch. 6 says Kcb + Ke "must" be considered only when Kc is needed on a daily basis for specific fields and years, and Ch. 5 calls dual best for real-time scheduling and microirrigation.
6. Zr and p choices within Table 22 ranges; p varying with ETc (limits 0.1-0.8); no season-long Zr growth rule in Ch. 8.
7. Units and rounding: all depths mm, ETo mm/d, Zr m; the source specifies no rounding. Rain below about 0.2 ETo ignored (Ch. 8); no effective-rain formula beyond P - RO.
8. Annex 8 irrigates the whole previous-day depletion, one trigger rule; the source does not cover deficit irrigation, irrigation intervals or system capacity.

## Verification log (2026-11-24)

Method: raw HTML downloaded for x0490e00/0a/0b/0c/0e/0p.htm; equation and figure GIFs downloaded and read as images. Base URL http://www.fao.org/4/x0490E/.

Corrections (old -> new):
- Table 12 notes "Kc mid adjustable by Eq. 62, Kc end by Eq. 65 (only if tabulated Kc end is at least 0.45)" -> the table notes do not mention Eqs. 62/65 or 0.45; these come from the Ch. 6 text. (x0490e0b.htm)
- Eq. 65 "the table note and text word the threshold slightly differently" -> both wordings ("exceed 0.45" and "K_c end >= 0.45") are in the Ch. 6 Kc end text. (x0490e0b.htm)
- Eq. 65 "same variable ranges" as Eq. 62 -> h range is 0.1 <= h <= 10 (inclusive) for Eq. 65 versus 0.1 < h < 10 for Eq. 62; u2/RHmin/h are late-season means (previously "not re-read"). (x0490e0b.htm)
- Kc ini "Inference: 0.6 applies to both crops; pepper row not re-checked" -> pepper cell also blank in raw markup, and Ch. 6 text states the single group value represents the whole group. (x0490e0b.htm)
- Eq. 60 on the table value "is a choice" -> Eq. 60 text explicitly allows the Table 12 value. (x0490e0b.htm)
- "Box 15 / Example 28 apply [premature harvest] to dry beans" -> they build the dry-bean curve and apply Eq. 66; no premature harvest. (x0490e0b.htm)
- Eq. 66 day numbering "the source does not say" -> i is defined as [1.. length of the growing season]; Annex 8 Box 8.1 day-of-year handling added. (x0490e0b.htm, x0490e0p.htm)
- Eq. 84 "source does not say whether Dr is start-of-day or end-of-day" -> Example 37 uses start-of-day depletion; Annex 8 footnote 11 uses depletion after the morning's wetting. (x0490e0e.htm, x0490e0p.htm)
- Eq. 87 "Dr = 1000 (thetaFC - theta) Zr" -> Dr,i-1 = 1000 (thetaFC - theta_i-1) Zr. (x0490e0e.htm)
- Example 38 "theta_sub" -> theta_sub,i-1. (x0490e0e.htm)
- "Ch. 8 says nothing about drip" -> nothing in the water balance; trickle appears only in the salt-toxicity text. (x0490e0e.htm)
- "P - RO is effective rain" (unlabelled) -> labelled Inference; source does not use the term. (x0490e0e.htm)
- Annex 8 "Box 8.1 formulas are images" -> they are HTML text; Figure 8.1 is three GIFs. (x0490e0p.htm)
- Annex 8 "Ks (Eq. 80)" -> Ks is Eq. 84 (column AJ); Eq. 80 is Kc adj (column AK). (x0490e0p.htm)
- Annex 8 "effect on Kc adj said to be small" attached to pre-irrigation stress -> that statement refers to before planting and near season end. (x0490e0p.htm)
- Annex 8 trigger "end-of-day depletion exceeds RAW" -> first-estimate depletion (AG) > allowable depletion (AF) in the formula; text says ">= RAW". (x0490e0p.htm)
- Annex 8 outputs "only in the figures" -> Figure 8.1 shows only 15-27 May; Figure 8.3 graph shows nine irrigation markers (approximate). (x0490e0p.htm, x0490e7e/7f/7g/7i.gif)
- Section 5 item 5 "single Kc is best for weekly or longer periods" -> quoted Ch. 5/Ch. 6 wording. (x0490e0a.htm, x0490e0b.htm)

Newly added, VERIFIED from images: Eq. 61 (x0490e2c.gif), Eq. 63 (x0490e2e.gif), Eq. 64 (x0490e2f.gif), Annex 8 Eq. 8-1 (x0490e5z.gif) and Eq. 8-3 (x0490e60.gif).

Confirmed unchanged against raw HTML or images: TOC chapter titles and /3/ -> /4/ 301 redirect; Eqs. 56, 57, 58, 80-83, 85, 86, 88 (HTML text); Eqs. 59, 62, 65, 66, 84 (images re-read); Table 11 tomato and pepper rows, including "25/30"; Table 12 Solanum group, tomato and pepper rows and footnotes 1-2; Table 19 (all rows, including printed "0-30"); Table 20; Table 22 tomato and pepper rows and footnote 1; p adjustment formula and 0.1 <= p <= 0.8 limits (Ch. 8 text); Ex. 26, 36, 38 values; Annex 8 inputs (dates, stage lengths, Kcb, height, TEW/REW/De, available water, Root min/max, fw, MAD), the last irrigation on day 225 and footnotes 4 and 10.

Not verified: Figures 29, 30 and 32 (curves not read); Annex 8 irrigation dates and depths beyond 27 May (only the graph is available, so marker positions are approximate); Annex 8 "initial De 18 mm" derivation (not given in the source).

## Sources

- TOC: http://www.fao.org/4/x0490E/x0490e00.htm (redirect from https://www.fao.org/3/x0490E/x0490e00.htm)
- Chapter 5: http://www.fao.org/4/x0490E/x0490e0a.htm
- Chapter 6 (Tables 11, 12, Eqs. 58-66): http://www.fao.org/4/x0490E/x0490e0b.htm
- Chapter 7 (Tables 19, 20 only): http://www.fao.org/4/x0490E/x0490e0c.htm
- Chapter 8 (Eqs. 80-88, Table 22): http://www.fao.org/4/x0490E/x0490e0e.htm
- Annex 8: http://www.fao.org/4/x0490E/x0490e0p.htm
