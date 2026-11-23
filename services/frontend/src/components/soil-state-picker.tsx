import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { plotHref } from "@/lib/format";
import { SOIL_STATES, soilLabel, type SoilState } from "@/lib/soil-state";
import { cn } from "@/lib/utils";

/** The soil the day before, as three links so it works without client JS and survives a refresh. */
export function SoilStatePicker({
  plotId,
  selected,
  labelledBy,
}: {
  plotId: string;
  selected: SoilState | null;
  /** Id of the visible text that names this group. */
  labelledBy: string;
}) {
  return (
    <div role="group" aria-labelledby={labelledBy} className="grid grid-cols-3 gap-2">
      {SOIL_STATES.map((state) => (
        <Link
          key={state}
          aria-current={state === selected ? "true" : undefined}
          href={`${plotHref(plotId)}?soil=${state}`}
          className={cn(
            buttonVariants({ variant: state === selected ? "default" : "outline", size: "lg" }),
            "h-12 text-base font-bold",
          )}
        >
          {soilLabel(state)}
        </Link>
      ))}
    </div>
  );
}
