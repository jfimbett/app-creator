"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { FormLabel, SourceLink } from "@/components/FormLabel";
import { StatePanel } from "@/components/StatePanel";
import { useDataSource } from "@/lib/source";
import type { FilingsResponse } from "@/lib/types";

type FormChoice = "both" | "annual" | "quarterly";
const CHOICES: { id: FormChoice; label: string }[] = [
  { id: "both", label: "Annual and quarterly" },
  { id: "annual", label: "Annual" },
  { id: "quarterly", label: "Quarterly" },
];

function coverageLine(data: FilingsResponse): string {
  const { from_date: from, to_date: to, note } = data.coverage;
  const range = from && to ? `Filed ${from} to ${to}, up to 10 years.` : "No filings in this window.";
  return note ? `${range} ${note}.` : range;
}

/** All 10-K and 10-Q filings of the window, newest first, with amendments labelled. */
export function FilingHistory({ data }: { data: FilingsResponse }) {
  const { href } = useDataSource();
  const [choice, setChoice] = useState<FormChoice>("both");
  const [amendments, setAmendments] = useState(true);

  const rows = useMemo(
    () =>
      data.history.filter((row) => {
        if (row.is_amendment && !amendments) return false;
        if (choice === "annual") return row.form.startsWith("10-K");
        if (choice === "quarterly") return row.form.startsWith("10-Q");
        return true;
      }),
    [data.history, choice, amendments],
  );

  return (
    <div className="flex flex-col gap-2 sm:gap-3">
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-table">
        <fieldset className="flex flex-wrap items-center gap-1">
          <legend className="float-left mr-2 text-muted">Form type</legend>
          {CHOICES.map((item) => (
            <label
              key={item.id}
              className="toggle"
            >
              <input type="radio" name="filing-forms" value={item.id} checked={choice === item.id} onChange={() => setChoice(item.id)} className="sr-only" />
              {item.label}
            </label>
          ))}
        </fieldset>
        <label className="inline-flex cursor-pointer items-center gap-1.5">
          <input type="checkbox" checked={amendments} onChange={(event) => setAmendments(event.target.checked)} className="h-4 w-4 accent-[var(--accent)]" />
          Include amendments
        </label>
      </div>
      <p data-testid="filing-coverage" className="text-table text-muted">
        {coverageLine(data)}
      </p>
      {rows.length === 0 ? (
        <StatePanel kind="empty" title="No filings of the selected type" message="Change the form type or include amendments." />
      ) : (
        <div className="table-box max-h-[70vh]">
          <table data-testid="filing-history" className="data-table">
            <caption className="sr-only">Filing history, newest first</caption>
            <thead>
              <tr>
                <th scope="col">Form</th>
                <th scope="col">Filed</th>
                <th scope="col">Period</th>
                <th scope="col" className="hidden sm:table-cell">Accession</th>
                <th scope="col">Open</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.accession} data-testid="filing-row" data-form={row.form}>
                  <td>
                    <FormLabel filing={row} />
                  </td>
                  <td className="tabular-nums">{row.filing_date}</td>
                  <td className={row.report_date ? "tabular-nums" : "text-muted italic"}>{row.report_date ?? "not stated"}</td>
                  <td className="code-id hidden text-muted sm:table-cell">{row.accession}</td>
                  <td>
                    <span className="inline-flex gap-3">
                      <Link href={href(`/companies/${data.cik}/filings/${row.accession}`)} aria-label={`Read ${row.form} filed ${row.filing_date}`}>
                        Read
                      </Link>
                      {row.document_url ? <SourceLink url={row.document_url} /> : <SourceLink url={row.index_url} label="Filing index" />}
                      {row.document_in_snapshot === false ? <span className="text-xs italic text-muted">link only in demo</span> : null}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
