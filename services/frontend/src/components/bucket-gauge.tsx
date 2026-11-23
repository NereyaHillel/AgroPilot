import { percentOf } from "@/lib/format";

/**
 * The soil bucket, drawn like a rain gauge: the water the root zone holds before irrigation,
 * the water that irrigation adds on top in a lighter shade, and the dashed line where irrigation
 * starts. The numbers come from the planner. This only draws them.
 */
export function BucketGauge({
  before,
  added,
  capacity,
  trigger,
}: {
  before: number;
  added: number;
  capacity: number;
  trigger: number;
}) {
  return (
    <div
      role="img"
      aria-label={`Soil holds ${Math.round(before)} of ${Math.round(capacity)} millimetres before irrigation${added > 0 ? `, and irrigation adds ${Math.round(added)}` : ""}. Irrigation starts below ${Math.round(trigger)}.`}
      className="relative h-36 w-14 shrink-0 overflow-hidden rounded-sm border-2 border-soil bg-card"
    >
      <div
        className="absolute inset-x-0 bottom-0 bg-water"
        style={{ height: `${percentOf(before, capacity)}%` }}
      />
      <div
        className="absolute inset-x-0 bg-water/35"
        style={{ bottom: `${percentOf(before, capacity)}%`, height: `${percentOf(added, capacity)}%` }}
      />
      <div className="gauge-ticks absolute inset-0" />
      <div
        className="absolute inset-x-0 border-t-2 border-dashed border-soil"
        style={{ bottom: `${percentOf(trigger, capacity)}%` }}
      />
    </div>
  );
}
