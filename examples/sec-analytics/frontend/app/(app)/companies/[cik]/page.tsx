"use client";

import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { AnalystLayout } from "@/components/AnalystLayout";
import { CompanyProfile } from "@/components/CompanyProfile";
import { CompanyTabs } from "@/components/CompanyTabs";
import { KeyFigures } from "@/components/KeyFigures";
import { LiveErrorPanel } from "@/components/LiveErrorPanel";
import { MetricExplorer } from "@/components/MetricExplorer";
import { Panel } from "@/components/Panel";
import { RevenueIncomeChart, type YearRange } from "@/components/RevenueIncomeChart";
import { InfoBadge } from "@/components/SourceBadge";
import { StatementTable } from "@/components/StatementTable";
import { StatePanel } from "@/components/StatePanel";
import { api } from "@/lib/api";
import { chartPoints, companyLine, reportingUnit } from "@/lib/display";
import { useDataSource } from "@/lib/source";
import type { FinancialsResponse, Line } from "@/lib/types";
import { useApiResource } from "@/lib/useApiResource";

const YEAR_CHOICES = [5, 6, 7, 8, 9, 10];
const SUMMARY_NOTE = "normalized summary from SEC Company Facts, not the complete filed statement";

function SummaryPanel({ id, title, lines, data }: { id: string; title: string; lines: readonly Line[]; data: FinancialsResponse }) {
  return (
    <Panel title={title} id={id} badge={<InfoBadge source={data.source} />}>
      <p className="mb-2 text-table text-muted">{SUMMARY_NOTE}</p>
      <StatementTable caption={`${title}, ${SUMMARY_NOTE}`} lines={lines} periods={data.periods} />
    </Panel>
  );
}

/** Company page: the SEC profile, key figures, chart, normalized statement summaries and the metric explorer. */
export default function CompanyPage() {
  const { cik } = useParams<{ cik: string }>();
  const router = useRouter();
  const { source, setSource, href } = useDataSource();
  const [range, setRange] = useState<YearRange>("all");
  const [years, setYears] = useState(10);
  const chartYears = range === "last5" ? 5 : undefined;
  const useDemo = useCallback(() => setSource("demo"), [setSource]);

  const loadProfile = useCallback((signal: AbortSignal) => api.getCompany(cik, { signal, source }), [cik, source]);
  const loadOverview = useCallback((signal: AbortSignal) => api.getOverview(cik, { signal, years: chartYears, source }), [cik, chartYears, source]);
  const loadFinancials = useCallback((signal: AbortSignal) => api.getFinancials(cik, { signal, years, source }), [cik, years, source]);
  const profile = useApiResource(`profile:${cik}:${source}`, loadProfile);
  const overview = useApiResource(`overview:${cik}:${range}:${source}`, loadOverview);
  const financials = useApiResource(`financials:${cik}:${years}:${source}`, loadFinancials);

  // Show the 10-digit CIK in the address (e.g. /companies/320193 → /companies/0000320193).
  const canonical = profile.status === "ok" ? profile.data.cik : null;
  useEffect(() => {
    if (canonical && canonical !== cik) router.replace(href(`/companies/${canonical}`));
  }, [canonical, cik, router, href]);

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
        <LiveErrorPanel error={profile.error} retry={profile.reload} what="company" source={source} useDemo={useDemo} />
      </section>
    );
  }

  const company = profile.data;
  const unit = overview.status === "ok" ? reportingUnit(overview.data.chart) : null;
  const chartTitle = unit ? `Revenue and net income, ${unit}, by fiscal year` : "Revenue and net income by fiscal year";
  const overviewBadge = overview.status === "ok" ? <InfoBadge source={overview.data.source} /> : null;

  return (
    <AnalystLayout
      heading={<h1 className="text-heading font-semibold">{companyLine({ name: company.name, ticker: company.tickers[0] ?? null, cik: company.cik })}</h1>}
      scope={{ kind: "company", cik: company.cik }}
    >
      <CompanyTabs cik={company.cik} active="overview" />

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-[minmax(0,5fr)_minmax(0,8fr)]">
        <Panel title="Profile" id="profile" className="lg:self-start" badge={<InfoBadge source={company.source} />}>
          <CompanyProfile profile={company} />
        </Panel>

        <div className="flex min-w-0 flex-col gap-3">
          <Panel title="Key figures" id="key-figures-panel" badge={overviewBadge}>
            {overview.status === "loading" ? <StatePanel kind="loading" title="Loading key figures…" rows={2} /> : null}
            {overview.status === "error" ? <LiveErrorPanel error={overview.error} retry={overview.reload} what="key figures" source={source} useDemo={useDemo} /> : null}
            {overview.status === "ok" ? <KeyFigures figures={overview.data.key_figures} /> : null}
          </Panel>

          <Panel title={chartTitle} id="revenue-income" badge={overviewBadge}>
            {overview.status === "loading" ? <StatePanel kind="loading" title="Loading the chart…" rows={6} /> : null}
            {overview.status === "error" ? <LiveErrorPanel error={overview.error} retry={overview.reload} what="chart" source={source} useDemo={useDemo} /> : null}
            {overview.status === "ok" ? (
              unit ? (
                <RevenueIncomeChart points={chartPoints(overview.data.chart)} unit={unit} range={range} onRangeChange={setRange} notes={overview.data.notes} />
              ) : (
                <StatePanel
                  kind="empty"
                  title="No annual revenue or net income found"
                  message={overview.data.notes.map((note) => (
                    <p key={note}>{note}</p>
                  ))}
                />
              )
            ) : null}
          </Panel>
        </div>
      </div>

      <section aria-labelledby="statements-title" className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 id="statements-title" className="text-[0.9375rem] font-semibold">
            Annual financial summaries
          </h2>
          <fieldset className="flex flex-wrap items-center gap-1 text-table">
            <legend className="float-left mr-2 text-muted">Years shown</legend>
            {YEAR_CHOICES.map((choice) => (
              <label
                key={choice}
                className={`cursor-pointer rounded-sm border px-2 py-0.5 has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-accent ${years === choice ? "border-accent bg-accent text-on-accent" : "border-line text-fg"}`}
              >
                <input type="radio" name="statement-years" value={choice} checked={years === choice} onChange={() => setYears(choice)} className="sr-only" />
                {choice}
              </label>
            ))}
          </fieldset>
        </div>
        {financials.status === "loading" ? <StatePanel kind="loading" title="Loading the statement summaries…" rows={8} /> : null}
        {financials.status === "error" ? <LiveErrorPanel error={financials.error} retry={financials.reload} what="statement summaries" source={source} useDemo={useDemo} /> : null}
        {financials.status === "ok" ? (
          financials.data.periods.length === 0 ? (
            <StatePanel
              kind="empty"
              title="No annual statement data found"
              message={financials.data.notes.map((note) => (
                <p key={note}>{note}</p>
              ))}
            />
          ) : (
            <>
              <div className="text-table text-muted">
                {financials.data.periods.length < years ? <p>{financials.data.periods.length} annual periods available.</p> : null}
                {financials.data.notes.map((note) => (
                  <p key={note} data-testid="statement-note" className="[overflow-wrap:anywhere]">
                    {note}
                  </p>
                ))}
              </div>
              <SummaryPanel id="income-statement" title="Income statement (summary)" lines={financials.data.statements.income} data={financials.data} />
              <SummaryPanel id="balance-sheet" title="Balance sheet (summary)" lines={financials.data.statements.balance} data={financials.data} />
              <SummaryPanel id="cash-flow" title="Cash flow (summary)" lines={financials.data.statements.cash_flow} data={financials.data} />
              <SummaryPanel id="ratios" title="Ratios" lines={financials.data.ratios} data={financials.data} />
              <p className="text-table text-muted">
                SEC sources:{" "}
                {financials.data.source.source_urls.map((url) => (
                  <a key={url} href={url} target="_blank" rel="noreferrer" className="mr-2 [overflow-wrap:anywhere]">
                    {url}
                  </a>
                ))}
              </p>
            </>
          )
        ) : null}
      </section>

      <Panel title="Metric explorer" id="explorer" badge={financials.status === "ok" ? <InfoBadge source={financials.data.source} /> : null}>
        <MetricExplorer cik={company.cik} source={source} years={years} />
      </Panel>
    </AnalystLayout>
  );
}
