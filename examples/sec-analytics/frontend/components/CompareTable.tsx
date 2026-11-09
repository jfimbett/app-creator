import { metricLabel, MONEY_METRICS } from "@/lib/compare-state";
import { cellText, fiscalYearEndLine, rowUnitCaption, SERIES_COLOURS, tableModel } from "@/lib/compare-view";
import { formatPeriod } from "@/lib/format";
import type { CompareResponse, CompareRow } from "@/lib/types";

/** The warnings line: each warning as an icon and words, in the warning colour. */
export function CompareWarnings({ response }: { response: CompareResponse }) {
  return (
    <div className="flex flex-col gap-1 text-table">
      <p data-testid="fiscal-year-ends" className="text-muted">
        {fiscalYearEndLine(response.companies)}
      </p>
      {response.warnings.length > 0 ? (
        <ul aria-label="Comparison warnings" className="flex flex-col gap-0.5">
          {response.warnings.map((warning) => (
            <li key={warning.code} data-testid="compare-warning" data-code={warning.code} className="text-warning">
              <span aria-hidden="true">⚠ </span>
              {warning.message}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

function cellTitle(ticker: string, row: CompareRow): string {
  const value = row.status === "ok" ? cellText(row) : `${cellText(row)}: ${row.reason ?? "no reason given"}`;
  return `${ticker} ${row.fiscal_year_label}, ${formatPeriod(row.period_start, row.period_end)}: ${value} (${row.kind}${row.indexed ? ", indexed" : ""})`;
}

/**
 * One line per company × metric, one column per fiscal year label. Each cell shows its value and, under it, that
 * company's own period end (MM-DD), because the companies' fiscal years end on different days.
 */
export function CompareTable({ response }: { response: CompareResponse }) {
  const model = tableModel(response);
  const indexing = response.index_base !== null;
  const colour = (cik: string) => SERIES_COLOURS[response.companies.findIndex((company) => company.cik === cik)];

  return (
    // relative: the screen-reader-only labels in the cells are absolutely positioned; without it they escape this
    // scroll box and widen the whole page at 390 px.
    <div className="table-box relative">
      <table className="data-table" data-testid="compare-table" data-points={model.points}>
        <caption className="sr-only">Comparison by each company&apos;s own fiscal year; each cell gives its own period end</caption>
        <thead>
          <tr>
            <th scope="col">Company · metric · unit</th>
            {model.labels.map((label) => (
              <th key={label} scope="col" className="num">
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {model.lines.map((line) => {
            const sample = Object.values(line.cells).find(Boolean);
            const indexed = sample?.indexed ?? false;
            const unit = rowUnitCaption(line.metric, sample?.unit ?? line.company.currency ?? "", indexed);
            const ticker = line.company.ticker || line.company.cik;
            return (
              <tr key={`${line.company.cik}-${line.metric}`} data-testid="compare-line" data-cik={line.company.cik} data-metric={line.metric}>
                <th scope="row" className="max-w-[9.5rem] whitespace-normal! py-1! text-left font-normal leading-tight sm:max-w-none sm:whitespace-nowrap!">
                  <span className="inline-flex flex-wrap items-center gap-x-1.5">
                    <span aria-hidden="true" className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: colour(line.company.cik) }} />
                    <span className="font-semibold">{ticker}</span>
                    <span>{metricLabel(line.metric)}</span>
                    <span className="text-muted">({unit})</span>
                    {indexed ? (
                      <span data-testid="indexed-badge" className="tag border-accent! text-accent!">
                        INDEXED
                      </span>
                    ) : null}
                    {indexing && !MONEY_METRICS.has(line.metric) ? (
                      <span data-testid="not-indexed" className="text-muted">
                        not indexed: ratio
                      </span>
                    ) : null}
                  </span>
                </th>
                {model.labels.map((label) => {
                  const row = line.cells[label];
                  if (!row) {
                    return (
                      <td key={label} className="num text-muted">
                        <span aria-hidden="true">·</span>
                        <span className="sr-only">no fiscal year {label} for {ticker}</span>
                      </td>
                    );
                  }
                  const ok = row.status === "ok";
                  return (
                    <td key={label} className="num" title={cellTitle(ticker, row)} data-testid="compare-cell" data-period-end={row.period_end}>
                      <span className={`block leading-4 ${ok ? "" : "text-muted"}`}>{cellText(row)}</span>
                      <span className="block text-[0.6875rem] leading-3 text-muted">{row.period_end.slice(5)}</span>
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
