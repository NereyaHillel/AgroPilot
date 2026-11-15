import "server-only";

/** The app is not set up: a service address is missing. Not a problem with a service. */
export class ConfigError extends Error {}

export type ServiceName = "registry" | "weather" | "planner";

const VARIABLES: Record<ServiceName, string> = {
  registry: "REGISTRY_URL",
  weather: "WEATHER_URL",
  planner: "PLANNER_URL",
};

/** Base URL of a service, without a trailing slash. A missing variable is a setup error. */
export function serviceUrl(service: ServiceName): string {
  const name = VARIABLES[service];
  const value = process.env[name]?.trim();
  if (!value) {
    throw new ConfigError(`${name} is not set. Copy .env.example to .env.local and set it.`);
  }
  return value.replace(/\/+$/, "");
}
