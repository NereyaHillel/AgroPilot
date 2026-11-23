/** How wet the soil was the day before the plan. The farmer must pick one; there is no default. */
export type SoilState = "dry" | "half" | "wet";

export const SOIL_STATES: readonly SoilState[] = ["dry", "half", "wet"];

const LABELS: Record<SoilState, string> = { dry: "Dry", half: "Half", wet: "Wet" };

export function soilLabel(state: SoilState): string {
  return LABELS[state];
}

/** Exact lowercase match only. A repeated or unknown value is null, never a guess. */
export function parseSoilState(value: string | string[] | undefined): SoilState | null {
  return typeof value === "string" && (SOIL_STATES as readonly string[]).includes(value)
    ? (value as SoilState)
    : null;
}
