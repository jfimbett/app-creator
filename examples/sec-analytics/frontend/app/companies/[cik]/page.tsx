"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { CompanyProfile } from "@/components/CompanyProfile";
import { KeyFigures } from "@/components/KeyFigures";
import { Panel } from "@/components/Panel";
import { RevenueIncomeChart, type YearRange } from "@/components/RevenueIncomeChart";
import { DEMO_LABEL, SourceBadge } from "@/components/SourceBadge";
import { StatePanel } from "@/components/StatePanel";
import { api, type ApiError } from "@/lib/api";
import { chartPoints, companyLine, reportingUnit } from "@/lib/display";
import type { SourceInfo } from "@/lib/types";
import { useApiResource } from "@/lib/useApiResource";

const HOME_LINK = (
  <p>
    Go back to the <Link href="/">list of demo companies</Link>, or search with <kbd className="rounded-sm border border-line px-1">/</kbd>.
  </p>
);

/** A failed API call as a state panel: offline, not in the snapshot, invalid CIK, or another error. */
function ProblemPanel({ error, retry, what }: { error: ApiError; retry: () => void; what: string }) {
  if (error.code === "backend_unreachable") return <StatePanel kind="offline" action={{ label: "Try again", onClick: retry }} />;
  if (error.code === "company_not_found") return <StatePanel kind="empty" title="Company not in the demo snapshot" message={<><p>{error.message}</p>{HOME_LINK}</>} />;
  if (error.code === "invalid_cik") return <StatePanel kind="error" title="This is not a valid CIK" message={<><p>{error.message}.</p>{HOME_LINK}</>} />;
  return <StatePanel kind="error" title={`Could not load the ${what}`} message={error.message} reference={error.reference} action={{ label: "Try again", onClick: retry }} />;
}

/** The API's source label; anything not marked as recorded SEC data is shown as synthetic, never as SEC data. */
function Badge({ source }: { source: SourceInfo }) {
  return source.label.startsWith(DEMO_LABEL) ? <SourceBadge kind="demo" label={source.label} /> : <SourceBadge kind="synthetic" label={source.label} />;
}

/** Company page: the SEC profile and the basic dashboard (key figures, chart and table). */
export default function CompanyPage() {
  const { cik } = useParams<{ cik: string }>();
  const router = useRouter();
  const [range, setRange] = useState<YearRange>("all");
  const years = range === "last5" ? 5 : undefined;

  const loadProfile = useCallback((signal: AbortSignal) => api.getCompany(cik, { signal }), [cik]);
  const loadOverview = useCallback((signal: AbortSignal) => api.getOverview(cik, { signal, years }), [cik, years]);
  const profile = useApiResource(`profile:${cik}`, loadProfile);
  const overview = useApiResource(`overview:${cik}:${range}`, loadOverview);

  // Show the 10-digit CIK in the address (e.g. /companies/320193 → /companies/0000320193).
  const canonical = profile.status === "ok" ? profile.data.cik : null;
  useEffect(() => {
    if (canonical && canonical !== cik) router.replace(`/companies/${canonical}`);
  }, [canonical, cik, router]);

  if (profile.status === "loading") {
    return (
      <section aria-label="Loading company" className="flex flex-col gap-3">
        <span className="skeleton h-6! w-72 max-w-full" />
        <StatePanel kind="loading" title="Loading company…" rows={8} />
      </section>
    );
  }
  if (profile.status === "error") {
    return (
      <section aria-labelledby="company-problem" className="flex max-w-2xl flex-col gap-3">
        <h1 id="company-problem" className="text-heading font-semibold">
          Company <span className="code-id">{cik}</span>
        </h1>
        <ProblemPanel error={profile.error} retry={profile.reload} what="company" />
      </section>
    );
  }

  const company = profile.data;
  const unit = overview.status === "ok" ? reportingUnit(overview.data.chart) : null;
  const chartTitle = unit ? `Revenue and net income, ${unit}, by fiscal year` : "Revenue and net income by fiscal year";
  const overviewBadge = overview.status === "ok" ? <Badge source={overview.data.source} /> : null;

  return (
    <div className="flex flex-col gap-3">
      <h1 className="text-heading font-semibold">{companyLine({ name: company.name, ticker: company.tickers[0] ?? null, cik: company.cik })}</h1>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-[minmax(0,5fr)_minmax(0,8fr)]">
        <Panel title="Profile" id="profile" className="lg:self-start" badge={<Badge source={company.source} />}>
          <CompanyProfile profile={company} />
        </Panel>

        <div className="flex min-w-0 flex-col gap-3">
          <Panel title="Key figures" id="key-figures-panel" badge={overviewBadge}>
            {overview.status === "loading" ? <StatePanel kind="loading" title="Loading key figures…" rows={2} /> : null}
            {overview.status === "error" ? <ProblemPanel error={overview.error} retry={overview.reload} what="key figures" /> : null}
            {overview.status === "ok" ? <KeyFigures figures={overview.data.key_figures} /> : null}
          </Panel>

          <Panel title={chartTitle} id="revenue-income" badge={overviewBadge}>
            {overview.status === "loading" ? <StatePanel kind="loading" title="Loading the chart…" rows={6} /> : null}
            {overview.status === "error" ? <ProblemPanel error={overview.error} retry={overview.reload} what="chart" /> : null}
            {overview.status === "ok" ? (
              unit ? (
                <RevenueIncomeChart points={chartPoints(overview.data.chart)} unit={unit} range={range} onRangeChange={setRange} notes={overview.data.notes} />
              ) : (
                <StatePanel
                  kind="empty"
                  title="No annual revenue or net income in the snapshot"
                  message={overview.data.notes.map((note) => (
                    <p key={note}>{note}</p>
                  ))}
                />
              )
            ) : null}
          </Panel>
        </div>
      </div>
    </div>
  );
}
