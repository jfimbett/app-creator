import type { Metadata } from "next";
import { Suspense } from "react";

import { AppHeader } from "@/components/AppHeader";
import { BackendStatus } from "@/components/BackendStatus";
import { CompanySearch } from "@/components/CompanySearch";
import { CompareLink } from "@/components/CompareLink";
import { ModeSelector } from "@/components/ModeSelector";
import { APP_NAME } from "@/lib/site";

import "./globals.css";

export const metadata: Metadata = {
  title: APP_NAME,
  description: `${APP_NAME}: company profiles and annual figures from SEC EDGAR data`,
};

/**
 * The shell: skip link, compact header, and one <main> for the page content.
 * Pages render sections inside this <main>; they do not add their own <main>.
 */
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" data-theme="dark">
      <body>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-30 focus:bg-panel-raised focus:px-2 focus:py-1"
        >
          Skip to content
        </a>
        {/* Suspense: these read the page URL (?source=), which is only known in the browser. */}
        <Suspense fallback={<AppHeader status={<BackendStatus />} />}>
          <AppHeader search={<CompanySearch />} nav={<CompareLink />} mode={<ModeSelector />} status={<BackendStatus />} />
        </Suspense>
        <main id="main" className="mx-auto w-full max-w-[1440px] px-4 py-4">
          <Suspense fallback={null}>{children}</Suspense>
        </main>
      </body>
    </html>
  );
}
