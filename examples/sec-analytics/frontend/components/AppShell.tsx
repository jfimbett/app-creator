import { Suspense, type ReactNode } from "react";

import { AppFooter } from "@/components/AppFooter";
import { AppHeader } from "@/components/AppHeader";
import { BackendStatus } from "@/components/BackendStatus";
import { HeaderSearch } from "@/components/HeaderSearch";
import { MainNav } from "@/components/MainNav";
import { ModeSelector } from "@/components/ModeSelector";

/**
 * The app's shell: header, one <main id="main"> for the screen, and the slim footer with the data disclaimer. Used by
 * the (app) route group layout and by the not-found page (which Next.js renders outside any route group).
 * Pages render sections inside this <main>; they do not add their own <main>.
 */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Suspense: these read the page URL (?source=), which is only known in the browser. */}
      <Suspense fallback={<AppHeader status={<BackendStatus />} />}>
        <AppHeader nav={<MainNav />} search={<HeaderSearch />} mode={<ModeSelector />} status={<BackendStatus />} />
      </Suspense>
      <main id="main" className="mx-auto w-full max-w-[1440px] flex-1 px-4 py-5">
        <Suspense fallback={null}>{children}</Suspense>
      </main>
      <AppFooter />
    </div>
  );
}
