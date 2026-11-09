"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useMemo, useState } from "react";

import { AnalystLayout } from "@/components/AnalystLayout";
import { CompanyChips } from "@/components/CompanyChips";
import { CompareChart } from "@/components/CompareChart";
import { ExportCsvButton, IndexToggle, MetricPicker, YearsPicker } from "@/components/CompareControls";
import { CompareTable, CompareWarnings } from "@/components/CompareTable";
import { LiveErrorPanel } from "@/components/LiveErrorPanel";
import { Panel } from "@/components/Panel";
import { InfoBadge } from "@/components/SourceBadge";
import { StatePanel } from "@/components/StatePanel";
import { api } from "@/lib/api";
import {
  addCompany,
  canCompare,
  companiesCutFromUrl,
  COUNT_RULE,
  type CompareState,
  NEED_TWO,
  parseCompareState,
  removeCompany,
  serializeCompareState,
  toggleMetric,
} from "@/lib/compare-state";
import type { CompareResponse, SearchResult } from "@/lib/types";
import { useApiResource } from "@/lib/useApiResource";

/**
 * The Compare screen (M4). Its whole state is in the URL, so a reload or a shared link shows the same
 * comparison. The backend builds the comparison; this page draws it.
 */
export default function ComparePage() {
  const params = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const state = useMemo(() => parseCompareState(new URLSearchParams(params.toString())), [params]);
  // A shared link with more than four companies keeps the first four and says so.
  const [message, setMessage] = useState<string | null>(() => (companiesCutFromUrl(new URLSearchParams(params.toString())) ? COUNT_RULE : null));
  const [known, setKnown] = useState<Record<string, { ticker: string; name: string }>>({});

  const update = useCallback(
    (next: CompareState) => router.replace(`${pathname}?${serializeCompareState(next)}`, { scroll: false }),
    [pathname, router],
  );

  const ready = canCompare(state);
  const key = serializeCompareState(state);
  const load = useCallback(
    (signal: AbortSignal) => (ready ? api.getCompare(parseCompareState(new URLSearchParams(key)), { signal }) : Promise.resolve(null)),
    [key, ready],
  );
  const result = useApiResource<CompareResponse | null>(`compare:${key}`, load);
  const data = result.status === "ok" ? result.data : null;

  const names = useMemo(() => {
    const merged = { ...known };
    for (const company of data?.companies ?? []) merged[company.cik] = { ticker: company.ticker, name: company.name };
    return merged;
  }, [known, data]);

  const add = (found: SearchResult) => {
    const outcome = addCompany(state, found.cik);
    setMessage(outcome.message);
    if (outcome.state !== state) {
      setKnown((current) => ({ ...current, [outcome.state.ciks.at(-1)!]: { ticker: found.ticker, name: found.name } }));
      update(outcome.state);
    }
  };

  return (
    <AnalystLayout
      heading={<h1 className="text-display font-semibold tracking-tight">Compare companies</h1>}
      scope={ready ? { kind: "comparison", ciks: [...state.ciks], metrics: [...state.metrics] } : null}
    >

      <section aria-label="Comparison settings" className="surface flex flex-col gap-3 p-4">
        <CompanyChips
          ciks={state.ciks}
          names={names}
          source={state.source}
          onAdd={add}
          onRemove={(cik) => {
            setMessage(null);
            update(removeCompany(state, cik));
          }}
          message={message}
          autoFocus={state.ciks.length === 0}
        />
        <MetricPicker selected={state.metrics} onToggle={(id) => update(toggleMetric(state, id))} />
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-line pt-3">
          <YearsPicker years={state.years} onChange={(years) => update({ ...state, years })} />
          <IndexToggle
            on={state.index === "first_common_year"}
            available={data ? data.index_available : null}
            metrics={state.metrics}
            onChange={(on) => update({ ...state, index: on ? "first_common_year" : "none" })}
          />
          <ExportCsvButton state={state} disabled={!data} />
        </div>
      </section>

      {!ready ? (
        <StatePanel
          kind="empty"
          title={NEED_TWO}
          message="Use the box above to add companies by name, ticker or CIK. The demo has Apple, Microsoft and Alphabet; Live mode has every SEC filer."
        />
      ) : result.status === "loading" ? (
        <StatePanel
          kind="loading"
          title={state.source === "live" ? `Loading ${state.ciks.length} companies from SEC (one request per second; up to two per company)…` : "Loading the comparison…"}
          rows={6}
        />
      ) : result.status === "error" ? (
        <LiveErrorPanel
          error={result.error}
          retry={result.reload}
          what="comparison"
          source={state.source}
          useDemo={() => update({ ...state, source: "demo" })}
        />
      ) : data ? (
        <>
          <Panel title="Comparison" badge={<InfoBadge source={data.source} />}>
            <div className="flex flex-col gap-3">
              <CompareWarnings response={data} />
              <CompareTable response={data} />
              <p className="text-table text-muted">
                Each company is shown by its own fiscal years (FY = year of the period end); nothing is aligned to calendar years or converted
                between currencies. Values may reflect later restatements; not point-in-time.
              </p>
            </div>
          </Panel>
          <Panel title="Chart" badge={<InfoBadge source={data.source} />}>
            <CompareChart key={data.metrics.join(",")} response={data} />
          </Panel>
        </>
      ) : null}
    </AnalystLayout>
  );
}
