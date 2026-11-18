# From irrigation depth (mm) to litres and run minutes on drip, and how irrigation is scheduled day by day

Method note: pages were read with WebFetch (returns a model-made extract, not raw text) or, for PDFs, with pdftotext on the downloaded file (UF/IFAS AE500, UF/IFAS HS917, FAO Irrigation Manual ch. 14 were read as real text). "Inference" or "my calculation" marks my own reasoning/arithmetic, not source text. The older project note (services/planner-service/docs/research/fao56.md) was used as a lead only; where I re-verified a point I say so.

## 1. Millimetres to litres, and drip application rate to run time

### Takeaway
1 mm of water over 1 m2 is exactly 1 litre, so depth (mm) x area (m2) = litres. A drip line's application rate in mm/h is emitter flow (L/h) divided by the soil area each emitter serves (row spacing x emitter spacing); run time = depth / rate. Examples: 1.0 L/h on 1.5 m x 0.4 m = 1.67 mm/h; 0.6 L/h on the same layout = 1.0 mm/h.

### Cited Findings
- 1 mm over 1 m2 = 1 L is unit arithmetic (1 m2 x 0.001 m = 0.001 m3 = 1 L). I found no source that states it in one sentence; a search confirmed that practical drip calculators rely on it: they divide emitter flow (L/h) by area per emitter (m2) to get mm/h, then divide daily requirement (mm/day) by rate (mm/h) to get hours — [Toro drip calculator](https://driptips.toro.com/drip-irrigation-calculator/) (example from search snippet: 4 L/h emitters at 0.40 x 0.60 m = about 16.7 mm/h; I did not open the page); also [WSU drip line rate calculator](https://irrigation.wsu.edu/Content/Calculators/Drip/Drip-Line-Rate.php) (snippet only).
- Same logic in extension practice, in US units: UF/IFAS AE500 computes the crop's daily water need in gal/acre, divides by the system's gal/hour/acre to get hours per day (run time = ETc / Q), then divides by application efficiency — [UF/IFAS AE500, Steps 3-6](https://journals.flvc.org/edis/article/download/131527/135108/236407) (archival copy, original April 2014).
- Worked examples (my calculation, formula rate = L/h / (row spacing x emitter spacing)):
  - 1.0 L/h, 1.5 m x 0.4 m: area per emitter 0.60 m2, rate 1.0/0.60 = 1.67 mm/h.
  - 0.6 L/h, same spacing: 0.6/0.60 = 1.00 mm/h.
  - Run time = depth / rate. 5 mm net at 1.67 mm/h = 3.0 h (180 min); 5 mm at 1.0 mm/h = 5.0 h.
  - Litres for a plot: 30 mm on a 200 m2 plot = 30 x 200 = 6000 L.
  - Same plot, check by emitter count: 200 m2 / 0.60 m2 = 333 emitters x 1.0 L/h = 333 L/h = 1.67 mm/h over 200 m2; 6000 L / 333 L/h = 18 h. (Consistent.)
- Wetting only part of the surface: drip wets a strip/bulb, not the whole surface. FAO-56 Table 20 gives the fraction of soil surface wetted, fw: trickle 0.3 to 0.4; precipitation, sprinkler, basin, border 1.0; furrow every furrow narrow bed 0.6-1.0, wide bed 0.4-0.6, alternate furrows 0.3-0.5 — [FAO-56 Ch. 7, Table 20](http://www.fao.org/4/x0490E/x0490e0c.htm) (re-verified by WebFetch this session; matches project note).
- FAO-56 text near Table 20 (WebFetch paraphrase/quotes): for drip "the value for fw may need to be reduced to about one-half to one-third of that given in Table 20" and a general approach is to multiply fw by [1 - (2/3) fc] for drip (fc = fraction of ground covered by canopy); evaporation is greater between plants, especially where only part of the surface is wetted — [FAO-56 Ch. 7](http://www.fao.org/4/x0490E/x0490e0c.htm). I could not check the exact wording on the page itself (extract only).
- FAO-56 Eq. 60 (Kc ini = fw x Kc ini(Table/Fig)) and Eq. 61 (Iw = I/fw, depth over the wetted part), Example 26 (trickle, fw about 0.4, Kc ini = 0.42) — [FAO-56 Ch. 6](http://www.fao.org/4/x0490E/x0490e0b.htm) as recorded in the project note; equation images were verified there per that note, but I did not re-fetch Ch. 6 this session (the fetch of that page was not completed).
- Annex 8 footnote 4: "The value for irrigation depth (divided by fw to express the depth over the wetted fraction of the soil, only)" — [FAO-56 Annex 8](http://www.fao.org/4/x0490E/x0490e0p.htm).
- Practical meaning: FAO's drip chapter says water "moves into the soil and wets the root zone vertically by gravity and laterally by capillary action. The planted area is only partially wetted", and most vegetables develop the bulk of their roots in the first 30 cm below the emission point — [FAO Irrigation Manual, Ch. 14 Drip irrigation](http://www.fao.org/4/a1336e/a1336e14a.pdf) (read as text via pdftotext).
- UC ANR drip scheduling slides multiply by fraction of soil volume wetted when working out the water that can be stored between irrigations: max inches of ETc between irrigations = rooting depth x available water capacity x fraction of soil volume wetted x allowable depletion — [UC ANR drip scheduling presentation](https://ucanr.edu/sites/default/files/2011-02/75715.pdf) (read via pdftotext; slide text partly garbled).

### Inferences
- Rate in mm/h from emitter spacing is a field-average (over the whole row x emitter cell), not the depth in the wetted strip. If a plan states a depth in field-average mm, the soil under the dripper receives roughly depth / fw (about 2.5-3x more). This is why Annex 8 divides by fw. Which "mm" a plan uses must be stated (field-average vs wetted-area).
- A real tomato crop at full cover on bed spacing of 1.5 m with 0.4 m emitters wets a band maybe 0.3-0.5 m wide; wetted fraction 0.3-0.4 of 1.5 m row spacing is about 0.45-0.6 m, consistent with Table 20. (Plausibility check, not sourced.)

### Gaps
- No single authoritative source for "1 mm = 1 L/m2" sentence; it is arithmetic.
- Eq. 60/61 and Example 26 not re-read this session; rely on project note.

## 2. FAO-56 Annex 8: how the daily schedule is calculated

### Takeaway
Annex 8 is a spreadsheet worked example for dry beans using the dual crop coefficient (Kcb + Ke). Each day it computes crop ET, updates root-zone depletion, and if depletion at the end of the day has reached the allowed limit, irrigates the next morning with an amount equal to that depletion (refill to field capacity). It assumes irrigation and rain arrive early in the morning.

### Cited Findings
- Dry bean dual-Kc example: Annex 8 "is applied to the dry, edible bean crop that was used in example boxes 15 and 16 of Chapters 6 and 7"; title per the table of contents: "Calculation example for applying the dual Kc procedure in irrigation scheduling" — [FAO-56 Annex 8](http://www.fao.org/4/x0490E/x0490e0p.htm); [FAO-56 TOC](http://www.fao.org/4/x0490E/x0490e00.htm) (title via project note).
- Timing: "The spreadsheet of Figure 8.1 presumes that all irrigation and precipitation events occur early in the morning." Footnote 10: "It is assumed that irrigation will be applied at the beginning of the following day." — [Annex 8](http://www.fao.org/4/x0490E/x0490e0p.htm).
- Trigger and amount: "The scheduling and magnitudes of irrigations are based on the soil water depletion at the end of the previous day." The net depth retained in the root zone "is exactly equal to the depletion depth" (i.e. refill to field capacity) — [Annex 8](http://www.fao.org/4/x0490E/x0490e0p.htm).
- Rain and drainage: "all drainage from the root zone due to excess precipitation occurs on the day of the precipitation event"; "It is assumed that runoff from precipitation is zero."; first-day irrigation presumed zero (footnote 4) — [Annex 8](http://www.fao.org/4/x0490E/x0490e0p.htm).
- Inputs, daily steps, MAD values (70% initial stage, 45% afterwards), fw irrigation 0.5, Zr growing in proportion to Kcb (0.2 to 0.8 m), trigger "depletion exceeds RAW", last irrigation by day 225, depletion computed via Eq. 85 then Ks (Eq. 80) when depletion exceeds RAW — from the project note's reading of Annex 8 (second-hand; Box 8.1 formulas are images and were not read by me) — [Annex 8](http://www.fao.org/4/x0490E/x0490e0p.htm); project note /home/nereya/AgroPilot/services/planner-service/docs/research/fao56.md section 4.
- Water balance behind it: Eq. 85, Dr,i = Dr,i-1 - (P - RO)i - Ii - CRi + ETc,i + DPi; term definitions confirmed by WebFetch: P precipitation, RO runoff, I "net irrigation depth on day i that infiltrates the soil", DP "water loss out of the root zone by deep percolation" — [FAO-56 Ch. 8, Soil water balance](http://www.fao.org/4/x0490E/x0490e0e.htm). Depletion is kept between 0 and TAW (Eq. 86), and DP is the excess when wetting goes beyond field capacity (Eq. 88) (project note).
- Single vs dual Kc: Ch. 5 (per project note) says the single Kc suits weekly or longer periods and planning, and dual Kc suits daily scheduling and high-frequency irrigation, because Ke captures the evaporation spike after each wetting — [FAO-56 Ch. 5](http://www.fao.org/4/x0490E/x0490e0a.htm) (project note; not re-read). Eq. 81 for single Kc under stress: ETc adj = Ks Kc ETo — [Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm) (project note).

### Inferences
- A single-Kc planner copies the Annex 8 skeleton (daily ETc, bucket, end-of-day check, next-morning refill, early-morning assumption, zero runoff) but drops Ke, the evaporation layer (TEW/REW/De), and daily Kcb adjustment; soil evaporation is folded into Kc. FAO itself flags this as less accurate for frequent wetting (Ch. 5; Ch. 6 footnote 1 on Kc ini rising with frequent wetting).
- Annex 8 uses MAD 70% early / 45% later for beans on a field with fw 0.5: it is a demonstration, not a drip-vegetable recommendation.
- Annex 8's rule "irrigate once depletion reaches the limit, then refill fully" is the large-infrequent pattern; it does not consider system capacity or irrigation time (project note gap 8).

### Gaps
- Annex 8's Box 8.1 formulas and the totals (number of irrigations, dates) were not read (images/figures).

## 3. Refill-to-field-capacity (large, infrequent) vs frequent small drip applications; typical practice for tomato and pepper; the 24-hour limit

### Takeaway
Extension and FAO guidance for drip-irrigated vegetables is frequent, small applications: roughly daily to several times a week, and several short cycles per day on sandy soils or at peak demand. Applications are limited to what the wetted root volume can hold, so single events of tens of mm are not the norm. When the required run time exceeds what the system can deliver, the standard response is to split into pulses, not lengthen the cycle.

### Cited Findings
- FAO Irrigation Manual (Drip irrigation): "In drip irrigation, water is applied to each plant separately in small, frequent, precise quantities"; soil moisture depletion "should not exceed 40 percent of the soil available moisture in the late growing stages of vegetables and fruit trees, and 20-30 percent in the early stages for vegetables. However, in order to obtain higher yields, the common practice is to irrigate every day in the later stages." Tensiometers 10 cbar (light soils) to 25 cbar (heavy soils) — [FAO Irrigation Manual Ch. 14](http://www.fao.org/4/a1336e/a1336e14a.pdf) (text read).
- FAO worked example (watermelon): irrigation is "at a fixed interval of one day" in late May, daily dose from gross 3.94 mm/d at peak; early in the season the interval is 2 to 4 days; drippers 4 L/h on 0.5 m — same document.
- UC ANR (drip scheduling slides): generic guideline is to deplete no more than 20-30% of available moisture in the active root zone; allowable depletion 0.2-0.3 in. (sandy loam), 0.3-0.6 in. (loam), 0.4-0.6 in. (clay loam); "irrigation frequency can vary from once a week early in the season to daily in sandy soils at full canopy"; "'typical' frequency is about every other day at full canopy" — [UC ANR 75715](https://ucanr.edu/sites/default/files/2011-02/75715.pdf) (pdftotext; slide text garbled but these lines legible).
- UF/IFAS HS917: irrigation amount must not exceed soil water holding capacity, "Otherwise, water is wasted and mobile nutrients are leached." For a 12-in. wetting width, 0.75 in/ft water holding capacity and 50% allowed depletion, the largest storable amounts are 24 gal/100 ft in the top 12 in., 36 gal in the top 18 in., 48 gal in the top 24 in.; in sandy soils the wetting front reached maximum rooting depth at about 80 gal/100 ft. Higher-adoption growers use a soil moisture tool rather than a fixed schedule — [UF/IFAS HS917](https://edis.ifas.ufl.edu/publication/HS917) (read via downloaded PDF at the URL returned for HS172; document header says HS917, original March 2003).
  - My calculation: 24 gal/100 ft on 6-ft bed centres = 90.8 L over 30.5 m x 1.83 m = 55.8 m2, about 1.6 mm field-average (36 gal about 2.4 mm; 48 gal about 3.3 mm; 80 gal about 5.4 mm). Per-event maximums on this plastic-mulch Florida sand are therefore a few mm, not 30-60 mm.
- UF/IFAS AE500 (tomato, pepper on plastic mulch): 12 in. emitter spacing, 13 gal/h/100 ft tape (0.13 gal/h per emitter), daily ETc about 0.13 in. (3.3 mm); run time 224 min/day at 100% and 264 min/day at 85% efficiency. Each cycle sized to refill 8-in. cylinder wetted bulb from 50% of plant available water to field capacity = 32 min; "264 min / 32.1 min = 8.22 cycles per day... rounded up to 9 cycles per day"; for a 12-in. root zone, six cycles of 48 min. "If the irrigation cycle run time is increased, then water and nutrients may be leached beyond the root zone" — [AE500](https://journals.flvc.org/edis/article/download/131527/135108/236407).
  - My calculation: 0.07 gal per cycle per emitter is about 0.48 mm per cycle on a 1 ft x 6 ft cell.
- Frequency range in a seed-company reproduction of UF guidance: drip frequency from once or twice weekly to several times daily depending on stage, weather and soil; sandy soils need smaller, more frequent applications — [Seminis, Water Management for Fresh Market Tomatoes](https://seminisus.s3.amazonaws.com/app/uploads/2020/02/9068_SE_S5_Water-Management-for-Fresh-Market-Tomatoes.pdf) (search-result snippet only; not opened; secondary).
- Root distribution under drip: most vegetable roots are in the first 30 cm below the emission point — FAO Ch. 14 above; UC ANR search-result summary says roots cluster near the wetted zone and a limited wetted volume can restrict root development (snippets; per a search summary of [UC/UF papers], not opened by me).
- Salinity: a UC ANR drip-salinity publication (found by search, not opened; URL candidates [ucanr.edu/media/307064](https://ucanr.edu/media/307064)) is summarised by the search as saying high-frequency drip keeps soil water and salinity fairly constant near the line, and salts accumulate toward the edge of the wetting pattern. I could not confirm the exact URL-to-claim mapping. FAO Ch. 14 has no salinity passage that I read.
- Rain: under plastic mulch rain contributes little and an irrigation may still be needed after small rain (HS917, Irrigation principle 3, link above).

### The 24-hour physical limit: what growers do
- Required hours = depth / rate. If this exceeds hours available (24 at the very most, less in practice for fertigation, flushing, pump or power windows and zones taking turns), options: (a) split into several shorter pulse cycles per day, as in AE500 (9 cycles of about 29 min each, or six x 48 min); (b) run more zones/higher flow (more or closer emitters or double tapes; AE500's pepper example uses two tapes at 54 gal/h/100 ft to cut run time to under 1 h/day for 0.12 in./day); (c) accept the crop is under-irrigated and monitor soil moisture; (d) change design (emitter flow, spacing). Option (a) with (b) is documented; (c) and (d) are my inference, not a cited statement. I found no source discussing "required depth exceeds 24 h" in those words.

### Inferences
- The more useful framing: tomato peak ETc about 5-7 mm/d needs 3-4 h at 1.67 mm/h at 90% efficiency, well within a day. A plan that must apply 30-60 mm in one go is replacing 6-12 days of daily ETc in one event. Frequent drip is chosen to keep the wetted volume in the sweet spot, cut deep percolation and nitrate leaching, avoid water stress swings and keep salt pushed outward (UC/UF/FAO above).
- Refill-to-field-capacity is not wrong as a water-balance bookkeeping rule (Annex 8, surface/sprinkler), but with drip the container is the wetted volume and is small.

### Gaps
- No source found giving a single universally accepted mm/event or events/week for drip tomato/pepper; ranges differ by soil, stage, climate. No peer-reviewed source opened for "frequent small outperform infrequent large" (search summary mentioned UF studies; not verified).

## 4. Irrigation efficiency, uniformity, net vs gross requirement

### Takeaway
Net requirement is the water the crop root zone must receive (ETc minus effective rain etc.). Gross requirement is the water the system must actually deliver: net divided by application efficiency (fraction as decimal). Drip is typically credited about 90% (range 80-95% depending on maintenance and water quality).

### Cited Findings
- FAO: drip "is the most advanced irrigation method with the highest application efficiency"; the worked example uses application efficiency 90% and computes gross = ETc x ... for 3.55 mm/d net peak (printed formula "3.55 x 0.90 ÷ 100 = 3.94 mm/d", as printed; the arithmetic as printed does not match a simple division by 0.9 and I flag it: 3.55/0.90 = 3.94, so the printed "x 0.90 / 100" is a layout artefact in the PDF text) — [FAO Irrigation Manual Ch. 14](http://www.fao.org/4/a1336e/a1336e14a.pdf).
- UF/IFAS: "A typical drip irrigation system can achieve a field application efficiency of 90%, while the maximum efficiency of typical sprinkler irrigation can achieve is 75%"; seepage 20-50%; for run time, "numbers ranging from 80% to 95% may be used" depending on maintenance and water quality; examples used 90% (pepper) and 85% (tomato); run time = net run time / efficiency — [AE500](https://journals.flvc.org/edis/article/download/131527/135108/236407).
- UC ANR uses a "drip system non-uniformity factor" (typical 1.1 to 1.2) multiplied into ETc to get irrigation requirement (example 0.14 in. x 1.15 = 0.16 in.) — [UC ANR 75715](https://ucanr.edu/sites/default/files/2011-02/75715.pdf).
- Emission uniformity (EU): per a search summary, EU compares the minimum to average emitter discharge and a UC extension drip-evaluation publication says EU of 90% or above is operating efficiently, with most tested systems at 80% or more (search snippet; source not opened) — via WebSearch; low confidence on exact document. NZ Landwise defines application efficiency as the share of applied water retained in the root zone, depending mainly on applied depth and distribution uniformity — [Landwise](https://www.landwise.org.nz/?p=1201) (snippet only).
- Gross = net / efficiency was also seen on a low-authority calculator (drip 85-95%) — not relied on.

### Inferences
- Definitions to explain: efficiency = how much applied water ends up in the root zone; uniformity = how evenly emitters deliver (a low-uniformity system must over-apply to adequately water the weakest emitters). 1/0.9 gives +11% to run times; at 80% efficiency +25%.
- With 30 mm net, gross at 90% is 33.3 mm: 20 h at 1.67 mm/h, 33 h at 1.0 mm/h.

### Gaps
- The FAO-56 itself has no drip efficiency table that I found. The FAO Consultant's guide (a1336e00) chapter 6 on net/gross depths was not readable in my fetch.

## 5. Effective rain

### Takeaway
FAO-56 Ch. 8 states small daily rain "is normally entirely evaporated" and "can usually be ignored in the water balance calculations", with the threshold about 0.2 ETo.

### Cited Findings
- Exact text (Ch. 8, "Soil water balance", subsection on precipitation, runoff and irrigation): "Daily precipitation in amounts less than about 0.2 ETo is normally entirely evaporated and can usually be ignored in the water balance calculations, especially when the single crop coefficient approach is being used." — [FAO-56 Ch. 8](http://www.fao.org/4/x0490E/x0490e0e.htm) (WebFetch extract, quoted by the tool).
- Larger rain: in the Eq. 85 balance, (P - RO) is counted and anything above field capacity leaves as deep percolation (Eq. 88); runoff estimated by "standard procedures from hydrological texts" — Ch. 8 (project note). Annex 8 assumes runoff zero and drainage the same day.
- With plastic mulch (Florida) rain contributes little and irrigation may still be required after small rain — HS917 principle 3.
- No effective-rain formula beyond P - RO appears in what I read (project note says the same). A drip row under canopy and mulch receives less of the rain than the field-average implies; I found no FAO text on this.

### Gaps
- No fraction-of-rain-counted rule (e.g. USDA-SCS) verified.

## 6. Project context: refill when depleted past half, 30-60 mm per event, 20-40 h run times

### Takeaway
As stated, it is hard to defend agronomically as a drip schedule. The arithmetic is right, but the amount per event is far above what the wetted root volume typically holds on sandy to medium soils, and well above the 20-40% allowable depletion FAO and UC give for drip vegetables. Frequent short applications are the usual alternative.

### Cited Findings and my calculations
- Run times (my calculation): 30 mm net at 1.67 mm/h = 18.0 h (20.0 h at 90% efficiency); 60 mm = 36 h (40 h gross). At 1.0 mm/h: 30 h net, 60 h net (33 h and 67 h gross). So 20-40 h corresponds to 30-60 mm only at the 1.67 mm/h rate with 90% efficiency; at 1.0 mm/h the same depths need 33-67 h, which is beyond 24 h and cannot be done in one run at all.
- Depletion fraction: the planner's "half" is higher than FAO's 40% max for late-stage drip vegetables and 20-30% early (FAO Ch. 14) and UC's 20-30% generic guideline; but FAO-56 Table 22 p = 0.40 (tomato) and 0.30 (bell pepper) (project note) are also below 0.5 for these crops.
- Event size vs storage: HS917's storable figure about 1.6-3.3 mm field-average on a 6-ft bed sandy soil (my conversion) and AE500's 0.5 mm per cycle in the 8-in. bulb example. FAO's TAW sizes (tomato Zr 0.7-1.5 m, 120-170 mm/m for silty soils, Table 22 and Example 36, project note) give a whole-profile TAW of 80-250 mm, so 30-60 mm is feasible as a balance number on a whole-field basis; the problem is the drip wets only fw 0.3-0.4 of the surface and a smaller root volume. 
  - Inference check: field-average depletion of 30-60 mm with fw 0.3-0.4 means 75-200 mm in the wetted strip, which would exceed a typical wetted-volume capacity (my estimate: 8-12 in. root depth x 8% PAW = 16-24 mm) and cause deep percolation.
- Practical effect on events: the plan implies one irrigation every 6-12 days at peak ETc 5 mm/d, whereas FAO says daily in late stages, UC says about every other day at full canopy, and UF/IFAS AE500 spreads the day into multiple pulses.
- Alternatives found in sources: (1) daily irrigation of the day's ETc / efficiency (FAO ch. 14 watermelon example; AE500 run-time method), (2) fixed interval of 1-4 days (FAO ch. 14), (3) multiple pulse cycles per day each sized to the wetted-bulb capacity (AE500), (4) soil-moisture triggers at 20-40% depletion (FAO ch. 14, UC), (5) a cap on depth per event equal to the wetted-zone capacity, with the planner's "bucket" sized by wetted volume (UC formula: rooting depth x AWC x fraction wetted x allowed depletion).
- Where the refill logic is defensible: for a simple bookkeeping tool, using whole-plot TAW with a refill rule is Annex 8's method; but Annex 8 targets surface irrigation with fw 0.5 and does not address system capacity (Annex 8; project note gap 8).

### Inferences
- A pragmatic fix is to keep the daily bucket but cap each event (and split into daily or several-times-per-week events), report run time in hours, and flag any plan above 24 h/day as infeasible.
- My numbers for wetted-volume capacity (16-24 mm) are an illustrative estimate from AE500's 8%-PAW example, not a sourced limit.

### Gaps
- No source evaluates a refill-to-FC-at-50% drip plan for vegetables directly; the conclusion rests on the combined guidance above.
- No verification of how the planner computes its rates; project files not examined beyond the two lead notes.
