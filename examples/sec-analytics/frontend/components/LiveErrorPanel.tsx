import Link from "next/link";

import { StatePanel } from "@/components/StatePanel";
import type { ApiError } from "@/lib/api";
import type { DataSourceChoice } from "@/lib/types";

const LIVE_FAILURES: Record<string, string> = {
  sec_contact_not_configured: "Live SEC data is not configured",
  sec_unavailable: "SEC is unavailable right now",
  sec_rate_limited: "SEC is limiting requests",
  sec_refused: "SEC refused the request",
  upstream_not_allowed: "SEC answered with an address the app does not follow",
  live_disabled: "Live data is off in this run of the app",
};

const HOME_LINK = (
  <p>
    Go back to the <Link href="/app">list of demo companies</Link>, or search with <kbd className="rounded-sm border border-line px-1">/</kbd>.
  </p>
);

type Props = {
  error: ApiError;
  retry: () => void;
  /** What could not be loaded, e.g. "chart". */
  what: string;
  source: DataSourceChoice;
  useDemo: () => void;
};

/**
 * A failed API call in words: what happened and what the person can do. A live failure never turns into demo data
 * by itself: the person chooses with "Use recorded demo data".
 */
export function LiveErrorPanel({ error, retry, what, source, useDemo }: Props) {
  if (error.code === "backend_unreachable") return <StatePanel kind="offline" action={{ label: "Try again", onClick: retry }} />;
  if (error.code === "company_not_found") {
    if (source === "live") return <StatePanel kind="empty" title="Not found at SEC" message={error.message} secondaryAction={{ label: "Use recorded demo data", onClick: useDemo }} />;
    return <StatePanel kind="empty" title="Company not in the demo snapshot" message={<><p>{error.message}</p>{HOME_LINK}</>} />;
  }
  if (error.code === "invalid_cik") return <StatePanel kind="error" title="This is not a valid CIK" message={<><p>{error.message}.</p>{HOME_LINK}</>} />;
  const title = LIVE_FAILURES[error.code];
  if (title) {
    return (
      <div data-testid="live-error" data-code={error.code}>
        <StatePanel
          kind="error"
          title={title}
          message={error.message}
          reference={error.reference}
          secondaryAction={{ label: "Use recorded demo data", onClick: useDemo }}
          action={{ label: "Try again", onClick: retry }}
        />
      </div>
    );
  }
  return <StatePanel kind="error" title={`Could not load the ${what}`} message={error.message} reference={error.reference} action={{ label: "Try again", onClick: retry }} />;
}
