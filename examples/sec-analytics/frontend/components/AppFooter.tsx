import Link from "next/link";

import { APP_NAME, DISCLAIMER } from "@/lib/site";

/** The slim app footer: the data disclaimer and a link back to the landing page (M6 §4.2, §6). */
export function AppFooter() {
  return (
    <footer className="mt-8 border-t border-line">
      <div className="mx-auto flex max-w-[1440px] flex-col gap-1 px-4 py-4 text-xs text-muted sm:flex-row sm:items-center sm:justify-between sm:gap-6">
        <p className="max-w-3xl" data-testid="app-disclaimer">{DISCLAIMER}</p>
        <Link href="/" className="shrink-0 text-link">
          About {APP_NAME}
        </Link>
      </div>
    </footer>
  );
}
