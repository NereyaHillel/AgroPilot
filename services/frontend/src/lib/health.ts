import "server-only";

import { ConfigError } from "./env";
import { getJson } from "./http";
import type { ServiceName } from "./env";

export type ServiceState = "up" | "down" | "not-set-up";
export type ServiceHealth = { service: ServiceName; label: string; state: ServiceState };

const SERVICES: { service: ServiceName; label: string }[] = [
  { service: "registry", label: "Registry" },
  { service: "weather", label: "Weather" },
  { service: "planner", label: "Planner" },
];

/** GET /health on each service. A service is up only if it answers {"status": "ok"}. */
export async function checkHealth(): Promise<ServiceHealth[]> {
  return Promise.all(
    SERVICES.map(async ({ service, label }): Promise<ServiceHealth> => {
      try {
        const body = await getJson<{ status?: string }>(service, "/health", 2000);
        return { service, label, state: body.status === "ok" ? "up" : "down" };
      } catch (error) {
        return { service, label, state: error instanceof ConfigError ? "not-set-up" : "down" };
      }
    }),
  );
}
