"use client";

import { useParams } from "next/navigation";
import { useCallback } from "react";

import { CompanyHeading } from "@/components/CompanyHeading";
import { CompanyTabs } from "@/components/CompanyTabs";
import { FilingHistory } from "@/components/FilingHistory";
import { LatestFilings } from "@/components/LatestFilings";
import { LiveErrorPanel } from "@/components/LiveErrorPanel";
import { Panel } from "@/components/Panel";
import { InfoBadge } from "@/components/SourceBadge";
import { StatePanel } from "@/components/StatePanel";
import { api } from "@/lib/api";
import { useDataSource } from "@/lib/source";
import { useApiResource } from "@/lib/useApiResource";

/** Filings view: the latest original reports and the filing history, from the chosen source. */
export default function FilingsPage() {
  const { cik } = useParams<{ cik: string }>();
  const { source, setSource } = useDataSource();
  const useDemo = useCallback(() => setSource("demo"), [setSource]);

  const loadProfile = useCallback((signal: AbortSignal) => api.getCompany(cik, { signal, source }), [cik, source]);
  const loadFilings = useCallback((signal: AbortSignal) => api.getFilings(cik, { signal, source }), [cik, source]);
  const profile = useApiResource(`profile:${cik}:${source}`, loadProfile);
  const filings = useApiResource(`filings:${cik}:${source}`, loadFilings);

  const canonical = filings.status === "ok" ? filings.data.cik : cik;

  return (
    <div className="flex flex-col gap-4">
      <CompanyHeading profile={profile.status === "ok" ? profile.data : null} cik={cik} />
      <CompanyTabs cik={canonical} active="filings" />
      {filings.status === "loading" ? <StatePanel kind="loading" title="Loading filings…" rows={8} /> : null}
      {filings.status === "error" ? <LiveErrorPanel error={filings.error} retry={filings.reload} what="filings" source={source} useDemo={useDemo} /> : null}
      {filings.status === "ok" ? (
        <>
          <LatestFilings cik={filings.data.cik} latest={filings.data.latest} />
          <Panel title="Filing history" id="filing-history-panel" badge={<InfoBadge source={filings.data.source} />}>
            <FilingHistory data={filings.data} />
          </Panel>
        </>
      ) : null}
    </div>
  );
}
