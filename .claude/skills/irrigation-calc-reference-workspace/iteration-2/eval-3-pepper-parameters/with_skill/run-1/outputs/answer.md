# Planner parameters: bell pepper, clay loam (200 mm/m)

Source: the "Planner-service plan rules" in the irrigation-calc-reference skill. These are the decided plan rules and they override the FAO-56 Table 22 values.

| Parameter | Value | Basis |
|---|---|---|
| Root depth Zr | **0.5 m** (fixed for bell pepper) | Plan rule. FAO-56 Zr max range 0.5-1.0 m is not used. |
| Bucket size TAW | **100 mm** | available_water_mm_per_m x Zr = 200 x 0.5. Comes from the registry, not from theta. |
| Trigger level | **50 mm** (0.5 x TAW) | Irrigate when the level would fall below 50 mm, i.e. depletion above 50 mm. Same for both crops. No Ks and no p adjustment (FAO p = 0.30 is not used). |
| Stage lengths (init / dev / mid / late) | **30 / 35 / 40 / 20 days** (125 days total) | Plan crop table. After day 125, hold Kc end. |
| Kc ini | **0.6** | Constant through the initial stage. No fw scaling. |
| Kc mid | **1.05** | Constant through the mid stage. No Eq. 62/65 climate adjustment. |
| Kc end | **0.90** | Reached at the end of the late stage and held afterwards. |

Kc curve: flat at 0.6 for days 1-30, linear 0.6 to 1.05 over days 31-65, flat at 1.05 for days 66-105, linear 1.05 to 0.90 over days 106-125, then 0.90.

Other relevant rules: the bucket starts full (L = TAW = 100 mm); each day L_pre = min(TAW, L_prev + rain - ETc); if L_pre < 50 then need = 100 - L_pre (refill to full), otherwise need = 0. Season day = (date - planting_date) + 1.

Note: the skill does not state the Kc used between day boundaries beyond Eq. 66 (linear interpolation in development and late stages), which is applied above.
