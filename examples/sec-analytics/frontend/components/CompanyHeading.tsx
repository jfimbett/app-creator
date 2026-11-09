import { InfoBadge } from "@/components/SourceBadge";
import { formatFiscalYearEnd } from "@/lib/format";
import type { CompanyProfile } from "@/lib/types";

/**
 * The company page header block: ticker badge, name as the page's <h1>, then CIK, SIC description, fiscal year end and
 * the profile's source badge. Every value is the SEC submissions file's own; a missing one is left out here (the
 * Profile panel says "Not reported by SEC"). While the profile loads, or when it failed, the heading is the CIK.
 */
export function CompanyHeading({ profile, cik }: { profile: CompanyProfile | null; cik: string }) {
  if (!profile) {
    return (
      <h1 className="min-w-0 text-heading font-semibold">
        Company <span className="code-id">{cik}</span>
      </h1>
    );
  }
  const ticker = profile.tickers[0] ?? null;
  const fiscalYearEnd = profile.fiscal_year_end ? formatFiscalYearEnd(profile.fiscal_year_end) : null;
  return (
    <div className="flex min-w-0 items-start gap-3">
      {ticker ? (
        <span className="mt-0.5 inline-flex h-7 shrink-0 items-center rounded-md border border-accent px-1.5 font-mono text-table font-semibold text-accent sm:h-9 sm:px-2 sm:text-title">{ticker}</span>
      ) : null}
      <div className="flex min-w-0 flex-col gap-1">
        <h1 className="text-heading font-semibold tracking-tight [overflow-wrap:anywhere] sm:text-display">{profile.name}</h1>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted sm:text-table">
          <span>
            CIK <span className="code-id text-fg">{profile.cik}</span>
          </span>
          {profile.sic_description ? <span>{profile.sic_description}</span> : null}
          {fiscalYearEnd ? (
            <span>
              Fiscal year ends <span className="code-id text-fg">{fiscalYearEnd}</span>
            </span>
          ) : null}
          <InfoBadge source={profile.source} />
        </div>
      </div>
    </div>
  );
}
