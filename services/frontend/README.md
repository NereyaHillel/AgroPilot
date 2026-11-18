# frontend

AgroPilot web app: farms and plots, and today's irrigation for each plot. Next.js (App Router), TypeScript, Tailwind CSS and shadcn/ui.

The browser never calls the services. Pages fetch on the server, and every call lives in `src/lib/` (`registry.ts`, `planner.ts`, `health.ts`).

## Run

```
cp .env.example .env.local    # REGISTRY_URL, WEATHER_URL, PLANNER_URL
npm install
npm run dev                   # http://localhost:3000
npm run build && npm run lint
```

Start registry-service, weather-service and planner-service first. A missing URL is reported on the page, and a service that is down is named on the page and in the status line at the foot.

## Pages

- `/` farms with their plots, each linking to its page
- `/plots/{id}` today's recommendation first, then the next 7 days. A stale forecast is marked next to the numbers it affects.

Design notes: a farm-supply sign, not a dashboard. Zilla Slab (the lettering of feed-store signs) for headings and big numbers, Atkinson Hyperlegible for text (designed for glare and low vision). Straw ground, soil-brown ink, field green for brand and links, blue only for water and the day to irrigate, marigold for stale data, barn red for errors. The scalloped edge under the header and the hard-edged sign plate around today's recommendation are the only decoration. The dashed line in every gauge is the planner's trigger, `trigger_mm` from the plan.
