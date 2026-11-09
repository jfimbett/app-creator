"use client";

import Link from "next/link";
import { useCallback } from "react";

import { CompanySearch } from "@/components/CompanySearch";
import { DemoCompanyCard } from "@/components/DemoCompanyCard";
import { LIVE_HELP } from "@/components/ModeSelector";
import { SourceBadge } from "@/components/SourceBadge";
import { StatePanel } from "@/components/StatePanel";
import { api } from "@/lib/api";
import { useDataSource } from "@/lib/source";
import { useApiResource } from "@/lib/useApiResource";

/** What a person can do once a company is open: the app's four views, in plain words (no new features). */
const HINTS = [
  { title: "Overview", text: "The SEC profile, key figures, revenue and net income by fiscal year, and statement summaries with the source of every value." },
  { title: "Filings", text: "The 10-K and 10-Q history, and a reader for annual reports with a section list and text search." },
  { title: "Compare", text: "Two to four companies side by side, each on its own fiscal years, with a CSV export.", link: "/compare" },
  { title: "Analyst", text: "Questions about the loaded figures and filings, answered with your own OpenRouter key and checked source links." },
] as const;

/** Home (/app): the search first, then the demo companies as cards (from GET /api/meta), then what you can do. */
export default function Home() {
  const loadMeta = useCallback((signal: AbortSignal) => api.getMeta({ signal }), []);
  const meta = useApiResource("meta", loadMeta);
  const { source, href } = useDataSource();
  const live = source === "live";

  return (
    <div className="flex flex-col gap-8">
      <section
        aria-labelledby="home-title"
        className="surface relative flex flex-col items-start gap-3 overflow-hidden px-5 py-8 sm:px-8 sm:py-10"
        style={{ backgroundImage: "radial-gradient(60rem 18rem at 0% 0%, var(--hero-glow), transparent 70%)" }}
      >
        <p className="label-caps text-accent">SEC EDGAR, explained</p>
        <h1 id="home-title" className="max-w-3xl text-display font-semibold tracking-tight">
          {live ? "Company profiles and annual figures from live SEC data" : "Company profiles and annual figures from recorded SEC filings"}
        </h1>
        <p className="max-w-2xl text-muted">
          Search by name, ticker or CIK. Press <kbd className="kbd">/</kbd> or <kbd className="kbd">Ctrl</kbd> <kbd className="kbd">K</kbd> (
          <kbd className="kbd">⌘</kbd> <kbd className="kbd">K</kbd> on a Mac) from any screen.
        </p>
        <div className="w-full max-w-2xl">
          <CompanySearch size="hero" />
        </div>
        {live ? <p className="max-w-2xl text-table text-muted">{LIVE_HELP}</p> : null}
      </section>

      <section aria-labelledby="demo-companies-title" id="demo-companies" className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 id="demo-companies-title" className="text-title font-semibold">
            Demo companies
          </h2>
          {meta.status === "ok" && !live ? <SourceBadge kind="demo" snapshotDate={meta.data.snapshot_date} /> : null}
        </div>
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
            <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {meta.data.demo_universe.map((company) => (
                <DemoCompanyCard key={company.cik} company={company} href={href(`/companies/${company.cik}`)} source={source} />
              ))}
            </ul>
          ) : (
            <StatePanel kind="empty" title="The snapshot lists no demo companies" message="Search by CIK, or switch to Live if it is offered." />
          )
        ) : null}
      </section>

      <section aria-labelledby="hints-title" className="flex flex-col gap-3">
        <h2 id="hints-title" className="text-title font-semibold">
          What you can do
        </h2>
        <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {HINTS.map((hint) => (
            <li key={hint.title} className="flex flex-col gap-1 border-l-2 border-accent pl-3">
              <h3 className="font-semibold">{"link" in hint ? <Link href={href(hint.link)}>{hint.title}</Link> : hint.title}</h3>
              <p className="text-table text-muted">{hint.text}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
