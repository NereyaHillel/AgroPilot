# Bell pepper, Mediterranean, transplant mid-April (FAO-56)

Source: FAO-56 Table 11 (stage lengths) and Table 12 (Kc), from memory, not re-checked against the document.

## Choices made
- Stage lengths: the Table 11 row for bell pepper "Europe and Mediterranean, April to June": 25 / 35 / 40 / 20 days, total 120 days. Table 11 also gives other rows (for example a longer California desert season, and a range for the initial stage). I picked the Mediterranean April row because it matches the climate and planting date.
- Kc values (Table 12): Kc ini 0.60, Kc mid 1.05, Kc end 0.90 for fully mature or dry fruit, or 0.80 for fresh-harvested fruit. I chose Kc end = 0.80 because bell pepper is normally picked fresh and green or colored.
- Kc ini 0.60 is the Table 12 tabulated value, which assumes frequent wetting. I used it as given. For drip irrigation with little wetted surface, Fig. 29/30 would give a lower value. I did not adjust it.
- Kc mid 1.05 is for sub-humid climate (RHmin about 45%, u2 about 2 m/s). Adjust it only if local data differ:
  Kc mid = 1.05 + [0.04(u2 - 2) - 0.004(RHmin - 45)] (h/3)^0.3, with h = 0.7 m. I did not apply this adjustment.
- Day 1 is the transplant day, 15 April. The Kc ini period is days 1-25.

## Values to load

| Stage | Length (days) | Season days | Kc |
|---|---|---|---|
| Initial | 25 | 1-25 | 0.60 |
| Development | 35 | 26-60 | linear 0.60 to 1.05 |
| Mid | 40 | 61-100 | 1.05 |
| Late | 20 | 101-120 | linear 1.05 to 0.80 |

Total: 120 days, ending about 12 August.

## Kc on the requested days
- Day 20 (4 May): initial stage, so Kc = 0.60.
- Day 50 (3 June): in development, 25 days past the end of the initial stage.
  Kc = 0.60 + (50 - 25)/35 x (1.05 - 0.60) = 0.60 + 0.3214 = 0.92 (0.921).

## Alternative
With Kc end = 0.90 (mature fruit), only the late stage changes. Days 20 and 50 are unaffected.
