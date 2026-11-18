import { connection } from "next/server";
import { checkHealth, type ServiceState } from "@/lib/health";

const TEXT: Record<ServiceState, string> = {
  up: "is up",
  down: "is down",
  "not-set-up": "is not set up",
};

/** Whether each service answers GET /health. Text as well as colour, so it reads in glare. */
export async function StatusLine() {
  await connection();
  const services = await checkHealth();
  return (
    <ul className="flex flex-wrap gap-x-5 gap-y-1 text-sm" aria-label="Service status">
      {services.map(({ service, label, state }) => (
        <li key={service} className="flex items-center gap-2">
          <span
            aria-hidden
            className={`inline-block size-2.5 rounded-full ${state === "up" ? "bg-field" : "bg-barn"}`}
          />
          <span>
            {label} {TEXT[state]}
          </span>
        </li>
      ))}
    </ul>
  );
}
