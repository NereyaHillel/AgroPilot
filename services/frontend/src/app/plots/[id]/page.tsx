import Link from "next/link";
import { notFound } from "next/navigation";
import { connection } from "next/server";
import { Suspense } from "react";
import { BucketGauge } from "@/components/bucket-gauge";
import { PlanTimeline, StaleBadge } from "@/components/plan-timeline";
import { ProblemNotice } from "@/components/problem-notice";
import { cropName, formatDuration, formatLongDate, formatMm, formatNumber, plotHref } from "@/lib/format";
import { isSetupProblem, userMessage } from "@/lib/http";
import { getPlan } from "@/lib/planner";
import { getPlot } from "@/lib/registry";
import type { Plan, Plot } from "@/lib/types";

export default async function PlotPage({ params }: PageProps<"/plots/[id]">) {
  await connection();
  const { id } = await params;
  const back = (
    <Link href="/" className="text-sm font-bold text-field underline underline-offset-4">
      All plots
    </Link>
  );

  let plot: Plot | null;
  try {
    plot = await getPlot(id);
  } catch (error) {
    const message = userMessage(error);
    if (message === null) throw error;
    return (
      <main className="mx-auto w-full max-w-5xl space-y-4 px-4 py-6 sm:px-6">
        {back}
        <ProblemNotice
          title="This plot is not available"
          detail={message}
          retryHref={plotHref(id)}
          setup={isSetupProblem(error)}
        />
      </main>
    );
  }
  if (!plot) notFound();

  return (
    <main className="mx-auto w-full max-w-5xl px-4 py-4 sm:px-6">
      {back}
      <h1 className="mt-2 font-heading text-3xl font-bold leading-tight">{plot.name}</h1>
      <p className="text-sm text-muted-foreground">
        {cropName(plot.crop_id)} planted {formatLongDate(plot.planting_date)}, {formatNumber(plot.area_m2)} m²
      </p>
      {/* The plot header shows at once; the plan streams in when the planner has answered. */}
      <Suspense fallback={<PlanPending />}>
        <PlanSection plotId={id} />
      </Suspense>
    </main>
  );
}

function PlanPending() {
  return (
    <div className="mt-5" aria-busy="true">
      <p className="font-heading text-5xl font-bold leading-[0.95] text-muted-foreground sm:text-6xl">
        Working out today&rsquo;s plan
      </p>
      <p className="mt-3 text-muted-foreground">Asking the registry and the forecast.</p>
    </div>
  );
}

async function PlanSection({ plotId }: { plotId: string }) {
  let plan: Plan;
  try {
    plan = await getPlan(plotId);
  } catch (error) {
    const message = userMessage(error);
    if (message === null) throw error;
    return (
      <div className="mt-6">
        <ProblemNotice
          title="Today's plan is not available"
          detail={message}
          retryHref={plotHref(plotId)}
          setup={isSetupProblem(error)}
        />
      </div>
    );
  }
  if (plan.days.length === 0) {
    return (
      <div className="mt-6">
        <ProblemNotice
          title="Today's plan is not available"
          detail="The planner answered without any days. Nothing is shown rather than a guess."
          retryHref={plotHref(plotId)}
        />
      </div>
    );
  }
  return <PlanView plan={plan} />;
}

function PlanView({ plan }: { plan: Plan }) {
  const today = plan.days[0];
  const waters = today.run_minutes > 0;
  const count = plan.days.length;
  return (
    <div className="mt-5 lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(0,28rem)] lg:gap-12">
      <section aria-labelledby="today" className="pb-6">
        <div className="sign-plate p-4">
          <h2
            id="today"
            className={`font-heading text-5xl font-bold leading-[0.95] sm:text-7xl ${waters ? "text-water" : ""}`}
          >
            {waters ? (
              <>
                Water for
                <br />
                {formatDuration(today.run_minutes)}
              </>
            ) : (
              <>
                No irrigation
                <br />
                today
              </>
            )}
          </h2>
          <div className="mt-4 flex items-end justify-between gap-4">
            <div className="min-w-0">
              <p className="tabular text-lg">
                {waters
                  ? `${formatNumber(today.litres)} litres, ${formatMm(today.need_mm)} over the plot`
                  : `Soil holds ${formatMm(today.bucket_end_mm)} of ${formatMm(plan.bucket_capacity_mm)}`}
              </p>
              {today.stale && (
                <p className="mt-2">
                  <StaleBadge />
                </p>
              )}
            </div>
            <BucketGauge
              level={today.bucket_end_mm}
              capacity={plan.bucket_capacity_mm}
              trigger={plan.trigger_mm}
            />
          </div>
        </div>
        <p className="mt-4 text-sm text-muted-foreground">
          The dashed line is where irrigation starts: {formatMm(plan.trigger_mm)} of {formatMm(plan.bucket_capacity_mm)}.
        </p>
      </section>

      <section aria-labelledby="week">
        <h2 id="week" className="mb-2 font-heading text-3xl font-semibold text-field">
          {count === 1 ? "Today" : `Next ${count} days`}
        </h2>
        <PlanTimeline plan={plan} />
      </section>
    </div>
  );
}
