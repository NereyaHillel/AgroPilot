import { percentOf } from "@/lib/format";

/**
 * The soil bucket, drawn like a rain gauge: how much water the root zone holds, and the
 * dashed line where irrigation starts. The numbers come from the planner. This only draws them.
 */
export function BucketGauge({
  level,
  capacity,
  trigger,
}: {
  level: number;
  capacity: number;
  trigger: number;
}) {
  return (
    <div
      role="img"
      aria-label={`Soil holds ${Math.round(level)} of ${Math.round(capacity)} millimetres. Irrigation starts below ${Math.round(trigger)}.`}
      className="relative h-36 w-14 shrink-0 overflow-hidden rounded-sm border-2 border-soil bg-card"
    >
      <div
        className="absolute inset-x-0 bottom-0 bg-water"
        style={{ height: `${percentOf(level, capacity)}%` }}
      />
      <div className="gauge-ticks absolute inset-0" />
      <div
        className="absolute inset-x-0 border-t-2 border-dashed border-soil"
        style={{ bottom: `${percentOf(trigger, capacity)}%` }}
      />
    </div>
  );
}
