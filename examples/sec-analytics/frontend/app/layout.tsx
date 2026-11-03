import type { Metadata } from "next";

import { AppHeader } from "@/components/AppHeader";
import { BackendStatus } from "@/components/BackendStatus";
import { CompanySearch } from "@/components/CompanySearch";
import { APP_NAME } from "@/lib/site";

import "./globals.css";

export const metadata: Metadata = {
  title: APP_NAME,
  description: `${APP_NAME}: company profiles and figures from recorded SEC EDGAR data`,
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
        <AppHeader search={<CompanySearch />} status={<BackendStatus />} />
        <main id="main" className="mx-auto w-full max-w-[1440px] px-4 py-4">
          {children}
        </main>
      </body>
    </html>
  );
}
