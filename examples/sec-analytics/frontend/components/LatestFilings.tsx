"use client";

import Link from "next/link";

import { FormLabel, SourceLink } from "@/components/FormLabel";
import { useDataSource } from "@/lib/source";
import type { FilingMeta, LatestFilings as Latest } from "@/lib/types";

function LatestCard({ cik, title, form, filing, amendedBy }: { cik: string; title: string; form: string; filing: FilingMeta | null; amendedBy: FilingMeta | null }) {
  const { href } = useDataSource();
  if (!filing) {
    return (
      <div data-testid={`latest-${form}`} className="surface p-3 sm:p-4">
        <h3 className="label-caps text-muted">{title}</h3>
        <p className="mt-1 text-muted">No original {form} was found in this list.</p>
      </div>
    );
  }
  return (
    <div data-testid={`latest-${form}`} className="surface flex flex-col gap-1.5 p-3 sm:gap-2 sm:p-4">
      <h3 className="label-caps text-muted">{title}</h3>
      <span className="text-title sm:text-heading">
        <FormLabel filing={filing} showOriginal />
      </span>
      <dl className="flex flex-wrap gap-x-4 gap-y-0.5 text-table">
        <div className="flex gap-1.5">
          <dt className="text-muted">Filed</dt>
          <dd className="tabular-nums">{filing.filing_date}</dd>
        </div>
        <div className="flex gap-1.5">
          <dt className="text-muted">Period</dt>
          <dd className="tabular-nums">{filing.report_date ?? "not stated by SEC"}</dd>
        </div>
        <div className="flex min-w-0 flex-wrap items-baseline gap-x-1.5">
          <dt className="text-muted">Accession</dt>
          <dd className="code-id text-xs [overflow-wrap:anywhere] sm:text-table">{filing.accession}</dd>
        </div>
      </dl>
      {amendedBy ? (
        <p data-testid="amended-by" className="text-table text-warning">
          Amended by{" "}
          <Link href={href(`/companies/${cik}/filings/${amendedBy.accession}`)} className="code-id">
            {amendedBy.accession}
          </Link>{" "}
          on {amendedBy.filing_date}
        </p>
      ) : null}
      <div className="mt-1 flex flex-wrap items-center gap-4">
        <Link href={href(`/companies/${cik}/filings/${filing.accession}`)} className="btn btn-primary no-underline hover:no-underline" aria-label={`Read ${filing.form} filed ${filing.filing_date}`}>
          Read
        </Link>
        {filing.document_url ? <SourceLink url={filing.document_url} /> : <SourceLink url={filing.index_url} label="Filing index" />}
      </div>
    </div>
  );
}

/** The most recent original reports. Its heading always says where "latest" comes from. */
export function LatestFilings({ cik, latest }: { cik: string; latest: Latest }) {
  return (
    <section aria-labelledby="latest-heading" className="flex flex-col gap-2 sm:gap-3">
      <h2 id="latest-heading" data-testid="latest-label" className="text-title font-semibold">
        {latest.label}
      </h2>
      <div className="grid grid-cols-2 gap-2 sm:gap-4">
        <LatestCard cik={cik} title="Annual report" form="10-K" filing={latest.annual} amendedBy={latest.annual_amended_by} />
        <LatestCard cik={cik} title="Quarterly report" form="10-Q" filing={latest.quarterly} amendedBy={latest.quarterly_amended_by} />
      </div>
    </section>
  );
}
