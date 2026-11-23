import { Badge } from "@/components/ui/badge";
import { dayParts, formatDuration, formatMm, formatNumber, percentOf } from "@/lib/format";
import type { Plan } from "@/lib/types";

export function StaleBadge() {
  return (
    <Badge
      variant="outline"
      className="h-auto border-marigold bg-marigold/20 px-2 py-0.5 text-sm text-marigold-ink"
      title="The weather forecast behind this day could not be refreshed"
    >
      Older forecast
    </Badge>
  );
}

/**
 * One row per day. The planner's first day is today by contract, so it is labelled so.
 * Water days are written in words; the bar shows the soil before irrigation, with what
 * irrigation adds on top in a lighter shade.
 */
export function PlanTimeline({ plan }: { plan: Plan }) {
  return (
    <ol className="border-t-2 border-soil">
      {plan.days.map((day, index) => {
        const waters = day.run_minutes > 0;
        const { weekday, date } = dayParts(day.date);
        const before = day.bucket_end_mm - day.need_mm;
        return (
          <li key={day.date} className="grid grid-cols-[4.75rem_1fr] gap-x-3 border-b border-dashed py-3">
            <div className="leading-tight">
              <p className="font-heading text-xl font-bold">{index === 0 ? "Today" : weekday}</p>
              <p className="text-sm text-muted-foreground">{date}</p>
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                <p className={`font-bold ${waters ? "text-water" : ""}`}>
                  {waters ? `Water for ${formatDuration(day.run_minutes)}` : "No irrigation"}
                </p>
                {day.stale && <StaleBadge />}
              </div>
              {waters && (
                <p className="tabular text-sm text-muted-foreground">
                  {formatNumber(day.litres)} litres, {formatMm(day.need_mm)}
                </p>
              )}
              <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
                <div
                  role="img"
                  aria-label={`Soil before irrigation: ${formatMm(before)} of ${formatMm(plan.bucket_capacity_mm)}${waters ? `, irrigation adds ${formatMm(day.need_mm)}` : ""}`}
                  className="relative h-3 w-60 max-w-full shrink-0 overflow-hidden rounded-sm border border-soil bg-card"
                >
                  <div
                    className="absolute inset-y-0 left-0 bg-water"
                    style={{ width: `${percentOf(before, plan.bucket_capacity_mm)}%` }}
                  />
                  <div
                    className="absolute inset-y-0 bg-water/35"
                    style={{
                      left: `${percentOf(before, plan.bucket_capacity_mm)}%`,
                      width: `${percentOf(day.need_mm, plan.bucket_capacity_mm)}%`,
                    }}
                  />
                  <div
                    className="absolute inset-y-0 border-l-2 border-dashed border-soil"
                    style={{ left: `${percentOf(plan.trigger_mm, plan.bucket_capacity_mm)}%` }}
                  />
                </div>
                <p className="tabular shrink-0 text-sm text-muted-foreground">
                  {formatMm(before)} in soil{waters ? `, +${formatMm(day.need_mm)}` : ""}
                </p>
              </div>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
