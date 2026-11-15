const NUMBER = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 });
const ONE_DECIMAL = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 1 });

export function formatNumber(value: number): string {
  return NUMBER.format(value);
}

export function formatMm(value: number): string {
  return `${ONE_DECIMAL.format(value)} mm`;
}

/** "38 minutes" below an hour, "2 h 5 min" from an hour up. Rounded to whole minutes. */
export function formatDuration(minutes: number): string {
  const total = Math.round(minutes);
  if (total < 60) return `${total} ${total === 1 ? "minute" : "minutes"}`;
  const hours = Math.floor(total / 60);
  const rest = total % 60;
  return rest === 0 ? `${hours} h` : `${hours} h ${rest} min`;
}

// Dates arrive as YYYY-MM-DD in the plot's local time. Format them as UTC so the
// browser or server time zone can never move them to another day.
function inUtc(isoDate: string, options: Intl.DateTimeFormatOptions): string {
  return new Date(`${isoDate}T00:00:00Z`).toLocaleDateString("en-GB", {
    ...options,
    timeZone: "UTC",
  });
}

/** Weekday and day-month as separate strings, so nothing depends on how a locale joins them. */
export function dayParts(isoDate: string): { weekday: string; date: string } {
  return {
    weekday: inUtc(isoDate, { weekday: "short" }),
    date: inUtc(isoDate, { day: "numeric", month: "short" }),
  };
}

export function formatLongDate(isoDate: string): string {
  return inUtc(isoDate, { day: "numeric", month: "long", year: "numeric" });
}

/** "bell-pepper" -> "Bell pepper" */
export function cropName(cropId: string): string {
  const words = cropId.replace(/-/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

/** value as a 0-100 share of capacity. A missing or zero capacity draws as empty, never NaN. */
export function percentOf(value: number, capacity: number): number {
  if (!Number.isFinite(value) || !Number.isFinite(capacity) || capacity <= 0) return 0;
  return Math.min(100, Math.max(0, (value / capacity) * 100));
}

export function plotHref(plotId: string): string {
  return `/plots/${encodeURIComponent(plotId)}`;
}
