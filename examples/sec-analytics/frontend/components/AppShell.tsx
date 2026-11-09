import { Suspense, type ReactNode } from "react";

import { AppHeader } from "@/components/AppHeader";
import { BackendStatus } from "@/components/BackendStatus";
import { CompanySearch } from "@/components/CompanySearch";
import { CompareLink } from "@/components/CompareLink";
import { ModeSelector } from "@/components/ModeSelector";

/**
 * The app's shell: header and one <main id="main"> for the screen. Used by the (app) route group layout and by
 * the not-found page (which Next.js renders outside any route group).
 * Pages render sections inside this <main>; they do not add their own <main>.
 */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <>
      {/* Suspense: these read the page URL (?source=), which is only known in the browser. */}
      <Suspense fallback={<AppHeader status={<BackendStatus />} />}>
        <AppHeader search={<CompanySearch />} nav={<CompareLink />} mode={<ModeSelector />} status={<BackendStatus />} />
      </Suspense>
      <main id="main" className="mx-auto w-full max-w-[1440px] px-4 py-4">
        <Suspense fallback={null}>{children}</Suspense>
      </main>
    </>
  );
}
