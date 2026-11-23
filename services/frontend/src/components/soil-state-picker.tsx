import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { plotHref } from "@/lib/format";
import { SOIL_STATES, soilLabel, type SoilState } from "@/lib/soil-state";
import { cn } from "@/lib/utils";

/** The soil the day before, as three links so it works without client JS and survives a refresh. */
export function SoilStatePicker({ plotId, selected }: { plotId: string; selected: SoilState | null }) {
  return (
    <div role="group" aria-label="Soil the day before" className="grid grid-cols-3 gap-2">
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
