"use client";

import Link from "next/link";
import { useCallback } from "react";

import { Panel } from "@/components/Panel";
import { LIVE_HELP } from "@/components/ModeSelector";
import { SourceBadge } from "@/components/SourceBadge";
import { StatePanel } from "@/components/StatePanel";
import { api } from "@/lib/api";
import { companyLine } from "@/lib/display";
import { useDataSource } from "@/lib/source";
import { useApiResource } from "@/lib/useApiResource";

/** Home: how to search, and the three demo companies as plain links (from GET /api/meta). */
export default function Home() {
  const loadMeta = useCallback((signal: AbortSignal) => api.getMeta({ signal }), []);
  const meta = useApiResource("meta", loadMeta);
  const { source, href } = useDataSource();
  const live = source === "live";

  return (
    <div className="flex flex-col gap-4">
      <section aria-labelledby="home-title" className="flex flex-col gap-1">
        <h1 id="home-title" className="text-heading font-semibold">
          {live ? "Company profiles and annual figures from live SEC data" : "Company profiles and annual figures from recorded SEC filings"}
        </h1>
        <p className="text-muted">
          Press <kbd className="rounded-sm border border-line px-1 text-fg">/</kbd> or{" "}
          <kbd className="rounded-sm border border-line px-1 text-fg">Ctrl</kbd>/<kbd className="rounded-sm border border-line px-1 text-fg">⌘</kbd>{" "}
          <kbd className="rounded-sm border border-line px-1 text-fg">K</kbd> to search by name, ticker or CIK, or pick a company below.
        </p>
        {live ? <p className="max-w-3xl text-muted">{LIVE_HELP}</p> : null}
      </section>

      <Panel
        title="Demo companies"
        id="demo-companies"
        className="max-w-3xl"
        badge={meta.status === "ok" && !live ? <SourceBadge kind="demo" snapshotDate={meta.data.snapshot_date} /> : null}
      >
        {meta.status === "loading" ? <StatePanel kind="loading" title="Loading the demo companies…" rows={3} /> : null}
        {meta.status === "error" ? (
          meta.error.code === "backend_unreachable" ? (
            <StatePanel kind="offline" action={{ label: "Try again", onClick: meta.reload }} />
          ) : (
            <StatePanel kind="error" title="Could not load the demo companies" message={meta.error.message} reference={meta.error.reference} action={{ label: "Try again", onClick: meta.reload }} />
          )
        ) : null}
        {meta.status === "ok" ? (
          meta.data.demo_universe.length > 0 ? (
            <ul className="flex flex-col">
              {meta.data.demo_universe.map((company) => (
                <li key={company.cik} className="border-b border-line py-1.5 last:border-b-0">
                  <Link href={href(`/companies/${company.cik}`)}>{companyLine(company)}</Link>
                </li>
              ))}
            </ul>
          ) : (
            <StatePanel kind="empty" title="The snapshot lists no demo companies" />
          )
        ) : null}
      </Panel>
    </div>
  );
}
