"use client";

import Link from "next/link";
import { memo, useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from "react";

import { FormLabel, SourceLink } from "@/components/FormLabel";
import { SectionNav } from "@/components/SectionNav";
import { InfoBadge } from "@/components/SourceBadge";
import { TextSearch } from "@/components/TextSearch";
import { useDataSource } from "@/lib/source";
import { type BlockMatches, findMatches, highlightSegments, matchesByBlock, stepMatch } from "@/lib/text-search";
import type { FilingBlock, FilingDocumentResponse } from "@/lib/types";

const BLOCK_CLASS: Record<FilingBlock["kind"], string> = {
  text: "my-2",
  heading: "mb-2 mt-6 text-title font-semibold text-fg",
  table_row: "border-b border-line/50 py-0.5 text-table text-fg",
};

/** One block. Filing text only ever becomes React text nodes here, so nothing in it can run. */
const ReaderBlock = memo(function ReaderBlock({ block, matches, current }: { block: FilingBlock; matches: BlockMatches | undefined; current: number | null }) {
  const segments = highlightSegments(block.text, matches);
  return (
    <p id={`block-${block.id}`} data-block-id={block.id} data-kind={block.kind} tabIndex={block.kind === "heading" ? -1 : undefined} className={`reader-target ${BLOCK_CLASS[block.kind]}`}>
      {segments.map((segment, index) =>
        segment.matchIndex === null ? (
          segment.text
        ) : (
          <mark key={index} className="search-hit" data-testid="search-hit" data-current={segment.matchIndex === current ? "true" : undefined}>
            {segment.text}
          </mark>
        ),
      )}
    </p>
  );
});

/** Groups neighbouring table rows, so each flattened table gets one muted "table" label. */
function groupBlocks(blocks: readonly FilingBlock[]): (FilingBlock | FilingBlock[])[] {
  const groups: (FilingBlock | FilingBlock[])[] = [];
  for (const block of blocks) {
    const last = groups[groups.length - 1];
    if (block.kind !== "table_row") groups.push(block);
    else if (Array.isArray(last)) last.push(block);
    else groups.push([block]);
  }
  return groups;
}

function ReaderHeader({ cik, data }: { cik: string; data: FilingDocumentResponse }) {
  const { href } = useDataSource();
  const { meta, amends, amended_by: amendedBy } = data;
  return (
    <section aria-label="About this filing" className="flex flex-col gap-1.5 border border-line bg-panel p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <FormLabel filing={meta} showOriginal />
        <InfoBadge source={data.source} />
      </div>
      <dl className="flex flex-wrap gap-x-5 gap-y-0.5 text-table">
        <div className="flex gap-1.5">
          <dt className="text-muted">Period</dt>
          <dd className="tabular-nums">{meta.report_date ?? "not stated by SEC"}</dd>
        </div>
        <div className="flex gap-1.5">
          <dt className="text-muted">Filed</dt>
          <dd className="tabular-nums">{meta.filing_date}</dd>
        </div>
        <div className="flex gap-1.5">
          <dt className="text-muted">Accession</dt>
          <dd className="code-id">{meta.accession}</dd>
        </div>
      </dl>
      <p data-testid="reader-scope" className="text-table text-muted">
        {data.scope}
      </p>
      {meta.is_amendment ? (
        <p data-testid="amendment-note" className="text-table text-warning">
          This is an amendment. It may change only part of the report.
          {amends ? (
            <>
              {" "}Original report:{" "}
              <Link href={href(`/companies/${cik}/filings/${amends.accession}`)} className="code-id">
                {amends.accession}
              </Link>
              .
            </>
          ) : (
            " The original report is not in this list."
          )}
        </p>
      ) : null}
      {amendedBy ? (
        <p data-testid="amended-by" className="text-table text-warning">
          Amended by{" "}
          <Link href={href(`/companies/${cik}/filings/${amendedBy.accession}`)} className="code-id">
            {amendedBy.accession}
          </Link>{" "}
          on {amendedBy.filing_date}. This page shows the original report.
        </p>
      ) : null}
      <p className="flex flex-wrap gap-3 text-table">
        <span data-testid="reader-source">
          <SourceLink url={data.source_link} />
        </span>
        <SourceLink url={meta.index_url} label="Filing index" />
      </p>
    </section>
  );
}

/** The reader: header, section rail, sticky search and the document's plain text. */
export function FilingReader({ cik, data }: { cik: string; data: FilingDocumentResponse }) {
  const [query, setQuery] = useState("");
  const [current, setCurrent] = useState(0);
  const deferredQuery = useDeferredValue(query);
  const result = useMemo(() => findMatches(data.blocks, deferredQuery), [data.blocks, deferredQuery]);
  const byBlock = useMemo(() => matchesByBlock(result.matches), [result.matches]);
  const groups = useMemo(() => groupBlocks(data.blocks), [data.blocks]);
  const column = useRef<HTMLDivElement>(null);
  const total = result.matches.length;

  useEffect(() => {
    if (total === 0) return;
    column.current?.querySelector('mark[data-current="true"]')?.scrollIntoView({ block: "center" });
  }, [current, result, total]);

  const step = useCallback((direction: 1 | -1) => setCurrent((position) => stepMatch(position, direction, total)), [total]);
  const changeQuery = useCallback((value: string) => {
    setQuery(value);
    setCurrent(0);
  }, []);
  const clear = useCallback(() => changeQuery(""), [changeQuery]);

  const jumpTo = useCallback((blockId: number) => {
    const target = document.getElementById(`block-${blockId}`);
    target?.scrollIntoView({ block: "start" });
    target?.focus({ preventScroll: true });
  }, []);

  /** The current match is passed only to its own block, so other blocks skip rendering. */
  const currentFor = (blockId: number): number | null => {
    const entry = byBlock.get(blockId);
    if (!entry) return null;
    return current >= entry.firstIndex && current < entry.firstIndex + entry.ranges.length ? current : null;
  };

  return (
    <div className="flex flex-col gap-3">
      <ReaderHeader cik={cik} data={data} />
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-[17rem_minmax(0,1fr)]">
        <SectionNav status={data.section_status} note={data.note} sections={data.sections} onJump={jumpTo} />
        <div className="min-w-0 border border-line bg-panel">
          <TextSearch query={query} onQuery={changeQuery} result={result} current={current} pending={query !== deferredQuery} onStep={step} onClear={clear} />
          <div ref={column} data-testid="filing-reader" className="reader-column px-4 pb-6 pt-2">
            {groups.map((group) =>
              Array.isArray(group) ? (
                <div key={`table-${group[0].id}`} data-testid="reader-table" className="my-3 border-l-2 border-line pl-2">
                  <span className="label-caps text-muted" aria-hidden="true">
                    table
                  </span>
                  {group.map((row) => (
                    <ReaderBlock key={row.id} block={row} matches={byBlock.get(row.id)} current={currentFor(row.id)} />
                  ))}
                </div>
              ) : (
                <ReaderBlock key={group.id} block={group} matches={byBlock.get(group.id)} current={currentFor(group.id)} />
              ),
            )}
            {data.truncated ? (
              <p data-testid="reader-truncated" className="mt-4 text-warning">
                The document was cut here. <SourceLink url={data.source_link} label="Read the rest on sec.gov" />
              </p>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
