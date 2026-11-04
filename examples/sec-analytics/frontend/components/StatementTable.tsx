"use client";

import { useEffect, useRef } from "react";

import { KindBadge } from "@/components/SourceBadge";
import { ValueCell } from "@/components/ValueCell";
import { formatDate, unitCaption } from "@/lib/format";
import type { Line, PeriodInfo } from "@/lib/types";

/**
 * One normalized summary table: a row per line and a column per annual period, newest on the right. Each value comes
 * from the backend with its status; this table only arranges and formats them. When the table is wider than its
 * box it opens scrolled to the newest year.
 */
export function StatementTable({ caption, lines, periods }: { caption: string; lines: readonly Line[]; periods: readonly PeriodInfo[] }) {
  const box = useRef<HTMLDivElement>(null);
  const columns = periods.length;
  useEffect(() => {
    if (box.current) box.current.scrollLeft = box.current.scrollWidth;
  }, [columns]);

  return (
    <div ref={box} className="table-scroll">
      <table className="data-table" data-testid="statement-table">
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr>
            <th scope="col">Line</th>
            {periods.map((period) => (
              <th key={period.end} scope="col" className="num normal-case whitespace-normal! min-w-[5.5rem] leading-tight py-1!">
                {period.fiscal_year_label} (ends {formatDate(period.end)})
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {lines.map((line) => (
            <tr key={line.metric_id}>
              <th scope="row" className="max-w-[8.5rem] whitespace-normal! text-left font-normal leading-tight sm:max-w-none sm:whitespace-nowrap!">
                <span className="inline-flex flex-wrap items-center gap-x-1.5">
                  {line.label}
                  {line.kind === "derived" ? <KindBadge kind="derived" /> : null}
                  <span className="text-label text-muted">{unitCaption(line.unit)}</span>
                </span>
              </th>
              {line.values.map((value) => (
                <td key={value.period_end} className="num">
                  <ValueCell metric={value} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
