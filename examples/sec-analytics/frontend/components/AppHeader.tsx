import Link from "next/link";
import type { ReactNode } from "react";

type AppHeaderProps = {
  /** The header search (CompanySearch). The header only reserves the space; it has no search logic. */
  search?: ReactNode;
  /** The data source: the mode badge and, under `npm run dev`, the Demo / Live selector. */
  mode?: ReactNode;
  /** Backend status indicator (BackendStatus). */
  status?: ReactNode;
};

/**
 * Compact app header: wordmark, search slot, the data source and backend status.
 * At 390 px the search drops to its own full-width row below the wordmark.
 * No menu items: there are no other screens.
 */
export function AppHeader({ search, mode, status }: AppHeaderProps) {
  return (
    <header className="sticky top-0 z-20 border-b border-line bg-panel">
      <div className="mx-auto flex max-w-[1440px] flex-wrap items-center gap-x-4 gap-y-2 px-4 py-2">
        <Link
          href="/"
          className="label-caps shrink-0 text-[0.8125rem] font-bold tracking-[0.14em] text-fg no-underline hover:text-accent hover:no-underline"
        >
          SEC ANALYTICS
        </Link>
        {search ? (
          <div data-testid="header-search-slot" className="order-last w-full min-w-0 md:order-none md:w-auto md:max-w-md md:flex-1">
            {search}
          </div>
        ) : null}
        <div className="ml-auto flex min-w-0 flex-wrap items-center justify-end gap-2">
          {mode}
          {status}
        </div>
      </div>
    </header>
  );
}
