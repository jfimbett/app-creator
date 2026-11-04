"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback } from "react";

import { CompanyTabs } from "@/components/CompanyTabs";
import { FilingReader } from "@/components/FilingReader";
import { SourceLink } from "@/components/FormLabel";
import { LiveErrorPanel } from "@/components/LiveErrorPanel";
import { StatePanel } from "@/components/StatePanel";
import { api, type ApiError } from "@/lib/api";
import { companyLine } from "@/lib/display";
import { useDataSource } from "@/lib/source";
import { useApiResource } from "@/lib/useApiResource";

const DOCUMENT_PROBLEMS: Record<string, string> = {
  document_not_in_snapshot: "This filing's document is not in the recorded demo snapshot",
  document_too_large: "This document is too large for the reader",
  document_unavailable: "This document cannot be shown here",
  filing_not_found: "This company has no such 10-K or 10-Q",
  invalid_accession: "This is not a valid accession number",
};

function DocumentProblem({ error, listHref }: { error: ApiError; listHref: string }) {
  const details = error.envelope.error.details as { source_link?: unknown; index_url?: unknown } | null;
  const link = typeof details?.source_link === "string" ? details.source_link : null;
  const index = typeof details?.index_url === "string" ? details.index_url : null;
  const empty = error.code === "document_not_in_snapshot";
  return (
    <div data-testid="document-problem" data-code={error.code}>
      <StatePanel
        kind={empty ? "empty" : "error"}
        title={DOCUMENT_PROBLEMS[error.code]}
        message={
          <>
            {empty ? <p>Nothing was fetched. The original is on sec.gov.</p> : <p>{error.message}</p>}
            <p className="mt-1 flex flex-wrap gap-3">
              {link ? <SourceLink url={link} /> : null}
              {index ? <SourceLink url={index} label="Filing index" /> : null}
              <Link href={listHref}>Back to the filing list</Link>
            </p>
          </>
        }
      />
    </div>
  );
}

/** Filing reader: one filing's sanitized text, or an honest explanation of why it cannot be shown. */
export default function FilingReaderPage() {
  const { cik, accession } = useParams<{ cik: string; accession: string }>();
  const { source, setSource, href } = useDataSource();
  const useDemo = useCallback(() => setSource("demo"), [setSource]);

  const loadProfile = useCallback((signal: AbortSignal) => api.getCompany(cik, { signal, source }), [cik, source]);
  const loadDocument = useCallback((signal: AbortSignal) => api.getFilingDocument(cik, accession, { signal, source }), [cik, accession, source]);
  const profile = useApiResource(`profile:${cik}:${source}`, loadProfile);
  const document = useApiResource(`document:${cik}:${accession}:${source}`, loadDocument);

  const company = profile.status === "ok" ? companyLine({ name: profile.data.name, ticker: profile.data.tickers[0] ?? null, cik: profile.data.cik }) : `Company ${cik}`;
  const listHref = href(`/companies/${cik}/filings`);

  return (
    <div className="flex flex-col gap-3">
      <h1 className="text-heading font-semibold">{company}</h1>
      <CompanyTabs cik={cik} active="filings" />
      <p className="text-table">
        <Link href={listHref}>← Filing list</Link>
      </p>
      {document.status === "loading" ? <StatePanel kind="loading" title="Loading the filing text…" rows={12} /> : null}
      {document.status === "error" ? (
        DOCUMENT_PROBLEMS[document.error.code] ? (
          <DocumentProblem error={document.error} listHref={listHref} />
        ) : (
          <LiveErrorPanel error={document.error} retry={document.reload} what="filing" source={source} useDemo={useDemo} />
        )
      ) : null}
      {document.status === "ok" ? <FilingReader key={document.data.meta.accession} cik={cik} data={document.data} /> : null}
    </div>
  );
}
