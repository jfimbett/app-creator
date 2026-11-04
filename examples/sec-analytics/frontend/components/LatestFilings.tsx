"use client";

import Link from "next/link";

import { FormLabel, SourceLink } from "@/components/FormLabel";
import { useDataSource } from "@/lib/source";
import type { FilingMeta, LatestFilings as Latest } from "@/lib/types";

function LatestCard({ cik, title, form, filing, amendedBy }: { cik: string; title: string; form: string; filing: FilingMeta | null; amendedBy: FilingMeta | null }) {
  const { href } = useDataSource();
  if (!filing) {
    return (
      <div data-testid={`latest-${form}`} className="border border-line bg-panel-raised p-3">
        <h3 className="label-caps text-muted">{title}</h3>
        <p className="mt-1 text-muted">No original {form} was found in this list.</p>
      </div>
    );
  }
  return (
    <div data-testid={`latest-${form}`} className="flex flex-col gap-1 border border-line bg-panel-raised p-3">
      <h3 className="label-caps text-muted">{title}</h3>
      <FormLabel filing={filing} showOriginal />
      <dl className="grid grid-cols-[auto_1fr] gap-x-3 text-table">
        <dt className="text-muted">Filed</dt>
        <dd className="tabular-nums">{filing.filing_date}</dd>
        <dt className="text-muted">Period</dt>
        <dd className="tabular-nums">{filing.report_date ?? "not stated by SEC"}</dd>
        <dt className="text-muted">Accession</dt>
        <dd className="code-id [overflow-wrap:anywhere]">{filing.accession}</dd>
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
      <div className="mt-1 flex flex-wrap gap-3">
        <Link href={href(`/companies/${cik}/filings/${filing.accession}`)} className="font-semibold" aria-label={`Read ${filing.form} filed ${filing.filing_date}`}>
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
    <section aria-labelledby="latest-heading" className="flex flex-col gap-2">
      <h2 id="latest-heading" data-testid="latest-label" className="text-[0.9375rem] font-semibold">
        {latest.label}
      </h2>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <LatestCard cik={cik} title="Annual report" form="10-K" filing={latest.annual} amendedBy={latest.annual_amended_by} />
        <LatestCard cik={cik} title="Quarterly report" form="10-Q" filing={latest.quarterly} amendedBy={latest.quarterly_amended_by} />
      </div>
    </section>
  );
}
