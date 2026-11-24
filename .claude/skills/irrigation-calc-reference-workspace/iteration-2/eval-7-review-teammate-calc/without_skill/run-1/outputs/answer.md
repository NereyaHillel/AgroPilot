# Review against FAO-56: `tomorrow_irrigation` (bell pepper, drip)

The constants are right: Kc mid = 1.05 for pepper (Table 12), p = 0.30 (Table 22), RAW = p·TAW (Eq. 83), and the Ks denominator `0.7 * taw` = (1 − p)·TAW (Eq. 84). The way they are combined has six FAO-56 problems, listed from worst to least serious.

## 1. The wetted fraction `fw` must not scale Kc (the biggest error)

`kc = 1.05 * fw` gives 0.37. With ET0 = 6 mm/day that is ETc ≈ 2.2 mm/day, when it should be ≈ 6.3 mm/day. The code underestimates crop water use by roughly 65%, and the bucket will dry out without the function ever triggering.

In FAO-56, `fw` (fraction of the surface wetted by irrigation) affects only **soil evaporation**. Transpiration does not depend on how much of the surface the emitters wet:
- With the single Kc approach, partial wetting is applied only in the **initial stage** (Eq. 60: Kc ini = fw × Kc ini from Fig. 29/30, using I/fw as the wetting depth). Kc mid and Kc end are **not** reduced for drip.
- With the dual approach (Kc = Kcb + Ke), `fw` enters through few = min(1 − fc, fw) (Eq. 75). That limits Ke. It never multiplies Kcb.

Sparse ground cover is a separate correction (based on fc, not fw). A pepper crop at full mid-season cover does not get one.

## 2. Kc is fixed at 1.05 for every day

Kc mid applies only in mid-season. FAO-56 uses a stage-based Kc curve: Kc ini = 0.6, a linear ramp through development, Kc mid = 1.05, then a linear decline to Kc end = 0.90 (Table 12, stage lengths from Table 11). The function needs the crop's day after planting (or the Kc for that day) as an input.

Kc mid (and Kc end when it is ≥ 0.45) should also get the climate adjustment (Eq. 62/65) whenever RHmin ≠ 45% or u2 ≠ 2 m/s:
Kc = Kc tab + [0.04(u2 − 2) − 0.004(RHmin − 45)]·(h/3)^0.3

## 3. Ks is computed but never used, and it uses the wrong depletion

- `ks` is a dead variable. Under stress FAO-56 uses ETc adj = Ks·Kc·ET0 (Eq. 80/81). The balance here always uses unstressed ETc, so once Dr > RAW the depletion grows too fast.
- Ks for a day should be based on the **start-of-day** depletion (Dr,i−1), not `dr_end`. Computing it from `dr_end` is circular, because dr_end itself depends on Ks.
- Ks is never bounded. If dr_end > TAW, Ks goes negative. Depletion cannot exceed TAW (0 ≤ Dr ≤ TAW, Eq. 86), so Ks stays between 0 and 1.

## 4. The water balance is incomplete and not bounded (Eq. 85–88)

FAO-56 Eq. 85: Dr,i = Dr,i−1 − (P − RO)i − Ii − CRi + ETc,i + DPi

- **Effective rain:** the code subtracts all of `rain`. Runoff (RO) has to come off first. At the very least, light rain (P under about 0.2·ET0) should be ignored, as FAO-56 suggests.
- **Lower bound and deep percolation:** a heavy rain makes `dr_end` negative. FAO-56 clamps Dr at 0 (the soil is at field capacity) and counts the excess as deep percolation (Eq. 88). The function hides this through `max(..., 0)` in the return, but it never produces a clamped Dr for the next day's balance. If a caller carries `dr_start - rain + etc` forward, it will have "negative depletion", which means water stored above field capacity.
- **Upper bound:** Dr ≤ TAW is not enforced.
- **Irrigation term:** no irrigation applied today (I) goes into the balance. If the plot was irrigated today, the next calculation starts from the wrong depletion.

## 5. p is not adjusted for the day's ETc

Table 22 values are for ETc ≈ 5 mm/day. FAO-56 adjusts p as p = p tab + 0.04·(5 − ETc), limited to 0.1 ≤ p ≤ 0.8. Hard-coding `0.30 * taw` and `0.7 * taw` gives a RAW that is too large on hot days and too small on cool days. Once p is adjusted, both RAW and the (1 − p) in Ks have to use the adjusted value.

## 6. Smaller points about the return value

- `max(dr_end, 0)` is redundant, because the branch only runs when dr_end > RAW ≥ 0.
- The amount returned is a **net** depth (a refill to field capacity, Dr → 0). FAO-56's balance works in net depths. Before converting to run time, divide by the application efficiency to get the gross depth.

## Corrected outline

```python
def tomorrow_irrigation(dr_start, et0, rain, runoff, taw, kc, p_tab=0.30):
    # kc: from the stage curve for that day (climate-adjusted Kc mid/end);
    # fw only enters through Kc ini (Eq. 60) or Ke (dual Kc), never here.
    etc = kc * et0
    p = min(max(p_tab + 0.04 * (5 - etc), 0.1), 0.8)
    raw = p * taw
    ks = 1.0 if dr_start <= raw else (taw - dr_start) / ((1 - p) * taw)
    etc_adj = ks * etc
    dr_end = min(max(dr_start - (rain - runoff) + etc_adj, 0.0), taw)
    return dr_end if dr_end > raw else 0.0   # net mm to refill to field capacity
```

Return or store the clamped `dr_end` as well, so the next day's balance starts from the right value.
