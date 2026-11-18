import "server-only";

import { getJson } from "./http";
import type { Plan } from "./types";

// The planner may wait for weather-service retries, so it gets more time than a plain lookup.
const TIMEOUT_MS = 20000;
const DAYS = 7;

/** The plan for the next days. Callers show plan.days.length, not DAYS. */
export function getPlan(plotId: string): Promise<Plan> {
  return getJson<Plan>(
    "planner",
    `/v1/plots/${encodeURIComponent(plotId)}/plan?days=${DAYS}`,
    TIMEOUT_MS,
  );
}
