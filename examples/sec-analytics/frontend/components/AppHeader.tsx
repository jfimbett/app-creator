import Link from "next/link";
import type { ReactNode } from "react";

import { BrandMark } from "@/components/BrandMark";
import { ThemeToggle } from "@/components/ThemeToggle";
import { APP_NAME } from "@/lib/site";

type AppHeaderProps = {
  /** Primary navigation (MainNav: Home and Compare). */
  nav?: ReactNode;
  /** The header search (HeaderSearch). It renders its own slot, or nothing on the home page. */
  search?: ReactNode;
  /** The data source: the mode badge and, under `npm run dev`, the Demo / Live selector. */
  mode?: ReactNode;
  /** Backend status indicator (BackendStatus). */
  status?: ReactNode;
};

/**
 * App header: brand (links to /app), primary nav, the search as the central control, then data source, backend
 * status and theme toggle grouped on the right. At 390 px it wraps: brand and nav, the status group, then the search
 * on its own full-width row; it is sticky from 768 px only, so a phone keeps its screen for content.
 */
export function AppHeader({ nav, search, mode, status }: AppHeaderProps) {
  return (
    <header className="z-20 border-b border-line bg-panel md:sticky md:top-0">
      <div className="mx-auto flex max-w-[1440px] flex-wrap items-center gap-x-4 gap-y-2 px-4 py-2 md:min-h-14">
        <Link href="/app" className="flex shrink-0 items-center gap-2 text-fg no-underline hover:text-fg hover:no-underline">
          <BrandMark />
          <span className="text-title font-semibold tracking-tight">{APP_NAME}</span>
        </Link>
        {nav ? <nav aria-label="Main">{nav}</nav> : null}
        {search}
        <div className="ml-auto flex min-w-0 flex-wrap items-center justify-end gap-2">
          {mode}
          {status}
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
