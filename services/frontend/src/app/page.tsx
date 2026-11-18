import Link from "next/link";
import { connection } from "next/server";
import { ProblemNotice } from "@/components/problem-notice";
import { cropName, formatNumber, plotHref } from "@/lib/format";
import { isSetupProblem, userMessage } from "@/lib/http";
import { listFarms, listPlots } from "@/lib/registry";

export default async function HomePage() {
  await connection();
  let farms, plots;
  try {
    [farms, plots] = await Promise.all([listFarms(), listPlots()]);
  } catch (error) {
    const message = userMessage(error);
    if (message === null) throw error;
    return (
      <main className="mx-auto w-full max-w-5xl px-4 py-6 sm:px-6">
        <ProblemNotice title="Plots are not available" detail={message} retryHref="/" setup={isSetupProblem(error)} />
      </main>
    );
  }

  // A plot whose farm is missing from the list still shows, under its own heading.
  const farmIds = new Set(farms.map((farm) => farm.id));
  const groups = farms.map((farm) => ({
    id: farm.id,
    name: farm.name,
    plots: plots.filter((plot) => plot.farm_id === farm.id),
  }));
  const loose = plots.filter((plot) => !farmIds.has(plot.farm_id));
  if (loose.length > 0) groups.push({ id: "other", name: "Other plots", plots: loose });

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-6 sm:px-6">
      <h1 className="font-heading text-5xl font-bold leading-none sm:text-6xl">Your plots</h1>
      {groups.length === 0 ? (
        <p className="mt-6 max-w-prose text-muted-foreground">
          There are no farms yet. Add a farm and its plots in the registry, and they appear here.
        </p>
      ) : (
        groups.map((group) => (
          <section key={group.id} className="mt-8" aria-labelledby={`farm-${group.id}`}>
            <h2 id={`farm-${group.id}`} className="font-heading text-3xl font-semibold text-field">
              {group.name}
            </h2>
            {group.plots.length === 0 ? (
              <p className="mt-2 text-muted-foreground">No plots on this farm yet.</p>
            ) : (
              <ul className="mt-2 border-t-2 border-soil">
                {group.plots.map((plot) => (
                  <li key={plot.id} className="border-b border-dashed">
                    <Link
                      href={plotHref(plot.id)}
                      className="flex min-h-16 flex-col justify-center border-l-4 border-transparent py-2 pl-3 hover:border-field hover:bg-secondary"
                    >
                      <span className="text-lg font-bold">{plot.name}</span>
                      <span className="text-sm text-muted-foreground">
                        {cropName(plot.crop_id)}, {formatNumber(plot.area_m2)} m²
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>
        ))
      )}
    </main>
  );
}
