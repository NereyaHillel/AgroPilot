import "server-only";

import { getJson, ServiceError } from "./http";
import type { Farm, Plot } from "./types";

const TIMEOUT_MS = 5000;

export function listFarms(): Promise<Farm[]> {
  return getJson<Farm[]>("registry", "/v1/farms", TIMEOUT_MS);
}

export function listPlots(): Promise<Plot[]> {
  return getJson<Plot[]>("registry", "/v1/plots", TIMEOUT_MS);
}

/** The plot, or null when the registry says it does not exist. */
export async function getPlot(id: string): Promise<Plot | null> {
  try {
    return await getJson<Plot>("registry", `/v1/plots/${encodeURIComponent(id)}`, TIMEOUT_MS);
  } catch (error) {
    // A malformed id is a 422 and an unknown one a 404: neither is a plot.
    if (error instanceof ServiceError && (error.status === 404 || error.status === 422)) {
      return null;
    }
    throw error;
  }
}
