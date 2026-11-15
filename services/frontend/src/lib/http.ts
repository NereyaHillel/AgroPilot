import "server-only";

import { ConfigError, serviceUrl, type ServiceName } from "./env";

/** What a service answered, or why we got no answer. Safe to show to the user. */
export class ServiceError extends Error {
  constructor(
    readonly service: ServiceName,
    readonly status: number | null,
    readonly code: string | null,
    message: string,
  ) {
    super(message);
  }
}

const SERVICE_LABEL: Record<ServiceName, string> = {
  registry: "registry-service",
  weather: "weather-service",
  planner: "planner-service",
};

/** GET a JSON document. Never cached: every page view shows current data. */
export async function getJson<T>(
  service: ServiceName,
  path: string,
  timeoutMs: number,
): Promise<T> {
  const label = SERVICE_LABEL[service];
  let response: Response;
  try {
    response = await fetch(`${serviceUrl(service)}${path}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(timeoutMs),
    });
  } catch (error) {
    if (error instanceof ConfigError) throw error;
    const timedOut = error instanceof Error && error.name === "TimeoutError";
    throw new ServiceError(
      service,
      null,
      null,
      timedOut ? `${label} did not answer in time` : `${label} is not reachable`,
    );
  }
  if (!response.ok) {
    // The services answer errors as application/problem+json with `detail` and `code`.
    let detail = `${label} answered with status ${response.status}`;
    let code: string | null = null;
    try {
      const problem = await response.json();
      if (typeof problem.detail === "string") detail = problem.detail;
      if (typeof problem.code === "string") code = problem.code;
    } catch {
      // Not JSON: keep the generic message.
    }
    throw new ServiceError(service, response.status, code, detail);
  }
  try {
    return (await response.json()) as T;
  } catch {
    throw new ServiceError(service, response.status, null, `${label} sent an unreadable answer`);
  }
}

export { SERVICE_LABEL };

/** Text that is safe to show a user when a service or the setup is the problem, else null. */
export function userMessage(error: unknown): string | null {
  return error instanceof ServiceError || error instanceof ConfigError ? error.message : null;
}

/** True when the problem is the app's own setup, which retrying cannot fix. */
export function isSetupProblem(error: unknown): boolean {
  return error instanceof ConfigError;
}
