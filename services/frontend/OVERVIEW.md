# frontend: overview

Port **3000**. The web app growers use. It lists farms and plots and shows, for each plot, today's irrigation recommendation and the next seven days. It is a thin presentation layer: all logic and data live in the backend services.

## Responsibilities

- `/` lists every farm with its plots; each plot links to `/plots/{id}`.
- `/plots/{id}` shows today's recommendation first and largest ("Water for 38 minutes" or "No irrigation today"), then the 7-day schedule.
- Mark stale weather data next to the numbers it affects.
- Show a clear, friendly message when a backend fails, naming which one.
- Show the live health of registry, weather and planner in a status line.

## Tech stack

Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, shadcn/ui (Base UI), lucide icons. The repo's `AGENTS.md` warns that this Next.js version differs from older ones, so read `node_modules/next/dist/docs/` before changing framework-level code.

## The key rule: server-side fetching only

The browser never calls `:8000`, `:8001` or `:8002`. Pages are Server Components, and every backend call lives in `src/lib/`, which imports `server-only` so it cannot be bundled into client code. Requests use `cache: "no-store"` so each page view shows current data.

## Code layout

| Path | Role |
|---|---|
| `src/app/page.tsx` | Farm and plot directory. Fetches farms and plots in parallel, groups plots by farm, and puts plots with an unknown farm under "Other plots" |
| `src/app/plots/[id]/page.tsx` | Plot page. Loads the plot, then streams the plan in with `Suspense`, so the header shows at once |
| `src/app/{error,loading,not-found}.tsx` | Fallback screens, so there is never a blank page or a stack trace |
| `src/lib/env.ts` | Reads `REGISTRY_URL`, `WEATHER_URL`, `PLANNER_URL`. A missing one is a `ConfigError`, not a service failure |
| `src/lib/http.ts` | `getJson`: timeouts, parsing of `problem+json` errors, `ServiceError` carrying the service name and a safe message |
| `src/lib/registry.ts`, `planner.ts`, `health.ts` | Typed API clients. Timeouts: registry 5 s, planner 20 s (it may wait for weather retries), health 2 s |
| `src/lib/types.ts`, `format.ts` | Response types and number, date and duration formatting |
| `src/components/` | `soil-state-picker` (Dry / Half / Wet links), `plan-timeline` (7-day table and stale badge), `bucket-gauge` (soil level against the trigger line), `problem-notice` (error banner), `status-line` (health bar), plus shadcn `ui/` pieces |

## How a plot page works

1. `getPlot(id)` asks the registry. A 404 or 422 shows the standard not-found page. A service problem shows an error notice with a retry link.
2. The header (name, crop, planting date, area) renders immediately.
3. The farmer picks Dry, Half or Wet for the soil the day before (`?soil=` in the URL, no default). Until then the page shows only that question. Then `getPlan(id, soil)` asks the planner for 7 days.
4. If `today.run_minutes > 0` the page shows "Water for N minutes" with litres and mm. Otherwise "No irrigation today" with how much water the soil holds.
5. A stale flag on today shows a warning badge beside the numbers. The timeline marks stale days the same way.
6. The gauge shows the soil level and a dashed line where irrigation triggers (`trigger_mm` from the plan).

The page uses the number of days the planner returned, not a hard-coded 7, because a stale forecast can give a shorter plan.

## Error handling

Services answer errors as `application/problem+json`. `getJson` turns each into a `ServiceError` with the service name and the `detail` text. Pages catch it and render a `ProblemNotice`: what happened, which service, and "Try again". Setup problems (a missing URL) are shown differently, with no retry, because waiting will not fix them. Anything that is not a known service or setup error falls through to `error.tsx`, which shows a generic message and a log reference, never the stack trace.

## Health bar

`StatusLine` calls `GET /health` on all three services in parallel. A service is "up" only if it answers `{"status": "ok"}`. It shows text as well as colour, so it reads in glare.

## Design

The look is a farm-supply sign, not a dashboard. Zilla Slab for headings and big numbers, Atkinson Hyperlegible for text. A straw background, soil-brown ink, field green for brand and links, blue only for water and the day to irrigate, marigold for stale data and barn red for errors. Today's recommendation sits in a hard-edged sign plate.

## Configuration

`.env.local` (git-ignored), documented in `.env.example`:

```
REGISTRY_URL=http://127.0.0.1:8000
WEATHER_URL=http://127.0.0.1:8001
PLANNER_URL=http://127.0.0.1:8002
```

## Run and verify

```
cp .env.example .env.local
npm install
npm run dev                  # http://localhost:3000
npm run build && npm run lint
```

Start the three backends first. The spec requires `build` and `lint` to finish with zero errors, and, at a 375 px viewport, no horizontal scroll and today's recommendation visible without scrolling. Those checks and their measured results still need to be recorded for the pull request.

## Known limits

- The frontend can only show what the planner computes. Because the planner assumes a full bucket on day 0, today's recommendation is usually "No irrigation today" until that assumption is replaced.
- Scope is deliberately two routes. There is no editing, login or settings page.
