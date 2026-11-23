"""Build the day-by-day plan for a plot from its registry data and a forecast."""

from crops import CROP_PLANS
from errors import ValidationProblem
from irrigation import (
    MAX_RUN_HOURS, START_FRACTION, TRIGGER_FRACTION, application_rate_mm_h, bucket_day, etc, kc_for_day, litres,
    run_minutes,
)
from schemas import Forecast, RegistryEmitter, RegistryPlot, RegistrySoil, SoilState


def build_plan(
    plot: RegistryPlot, soil: RegistrySoil, emitter: RegistryEmitter, forecast: Forecast, days: int, soil_state: SoilState
) -> dict:
    crop = CROP_PLANS.get(plot.crop_id)
    if crop is None:
        raise ValidationProblem(f"Crop {plot.crop_id!r} has no irrigation parameters")
    stages = crop.stages
    season_length = stages.ini + stages.dev + stages.mid + stages.late

    taw = soil.available_water_mm_per_m * crop.zr_m
    level = START_FRACTION[soil_state] * taw  # the farmer's answer for the day before
    max_apply_mm = MAX_RUN_HOURS * application_rate_mm_h(emitter.flow_lph, plot.row_spacing_m, plot.emitter_spacing_m)
    refilling = False
    plan = []
    for day in forecast.days[:days]:
        # Season day 1 is the planting date. Outside the season the curve holds its end values.
        season_day = min(max((day.date - plot.planting_date).days + 1, 1), season_length)
        kc = kc_for_day(season_day, stages, crop.kc_ini, crop.kc_mid, crop.kc_end)
        result = bucket_day(level, taw, day.rain_mm, etc(kc, day.et0_mm), max_apply_mm, refilling)
        level, refilling = result.level_end, result.refilling
        plan.append(
            {
                "date": day.date,
                "et0_mm": day.et0_mm,
                "kc": round(kc, 3),
                "need_mm": round(result.need_mm, 2),
                "litres": round(litres(result.need_mm, plot.area_m2), 2),
                "run_minutes": round(
                    run_minutes(result.need_mm, emitter.flow_lph, plot.row_spacing_m, plot.emitter_spacing_m), 2
                ),
                "stale": forecast.stale,
                "bucket_end_mm": round(level, 2),
            }
        )
    return {
        "bucket_capacity_mm": round(taw, 2),
        "trigger_mm": round(TRIGGER_FRACTION * taw, 2),
        "days": plan,
    }
