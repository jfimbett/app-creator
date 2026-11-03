import type { ReactNode } from "react";

import { uniqueInOrder } from "@/lib/display";
import { formatDate, formatFiscalYearEnd, NOT_REPORTED } from "@/lib/format";
import type { CompanyProfile as Profile } from "@/lib/types";

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="min-w-0 border-b border-line py-1.5">
      <dt className="label-caps text-muted">{label}</dt>
      <dd className="mt-0.5 [overflow-wrap:anywhere]">{children}</dd>
    </div>
  );
}

function orNotReported(value: string | null): ReactNode {
  return value ?? <span className="text-muted">{NOT_REPORTED}</span>;
}

function list(values: readonly string[]): ReactNode {
  return values.length > 0 ? values.join(", ") : <span className="text-muted">{NOT_REPORTED}</span>;
}

/**
 * The SEC identifiers exactly as in the submissions file. Missing fields say "Not reported by SEC".
 * There is no description, logo or website text: none of it is in the data.
 */
export function CompanyProfile({ profile }: { profile: Profile }) {
  return (
    <div data-testid="company-profile">
      <dl className="grid grid-cols-1 gap-x-6 sm:grid-cols-2">
        <Field label="Name">{profile.name}</Field>
        <Field label="CIK">
          <span className="code-id">{profile.cik}</span>
        </Field>
        <Field label="Tickers">{list(profile.tickers)}</Field>
        <Field label="Exchange">{list(uniqueInOrder(profile.exchanges))}</Field>
        <Field label="SIC code">{profile.sic ? <span className="code-id">{profile.sic}</span> : orNotReported(null)}</Field>
        <Field label="SIC description">{orNotReported(profile.sic_description)}</Field>
        <Field label="Fiscal year-end (MM-DD)">
          {profile.fiscal_year_end ? <span className="code-id">{formatFiscalYearEnd(profile.fiscal_year_end)}</span> : orNotReported(null)}
        </Field>
        <Field label="State of incorporation">{orNotReported(profile.state_of_incorporation)}</Field>
      </dl>
      <h3 className="label-caps mt-3 text-muted">Former names</h3>
      {profile.former_names.length > 0 ? (
        <div className="table-scroll mt-1">
          <table className="data-table">
            <thead>
              <tr>
                <th scope="col">Name</th>
                <th scope="col" className="num">From</th>
                <th scope="col" className="num">To</th>
              </tr>
            </thead>
            <tbody>
              {profile.former_names.map((former) => (
                <tr key={`${former.name}-${former.from}`}>
                  <td>{former.name}</td>
                  <td className="num">{formatDate(former.from)}</td>
                  <td className="num">{formatDate(former.to)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="mt-1 text-muted">{NOT_REPORTED}</p>
      )}
    </div>
  );
}
