import type { Metadata } from "next";

import { APP_NAME } from "@/lib/site";
import { THEME_INIT_SCRIPT } from "@/lib/theme";

import "./globals.css";

export const metadata: Metadata = {
  title: { default: APP_NAME, template: `%s · ${APP_NAME}` },
  description: `${APP_NAME}: company profiles and annual figures from SEC EDGAR data`,
};

/**
 * Root layout: <html>, <body>, the skip link and the global styles. The app shell lives in app/(app)/layout.tsx,
 * the landing page's header and footer in app/(marketing)/layout.tsx. Both render one <main id="main">.
 *
 * Theme: the inline script in <head> sets <html data-theme> from localStorage before the first paint, so a
 * light-theme visitor never sees a dark flash. Server rendering assumes dark (the :root colours in globals.css).
 * suppressHydrationWarning: the script changes that one attribute before React hydrates.
 */
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-30 focus:bg-panel-raised focus:px-2 focus:py-1"
        >
          Skip to content
        </a>
        {children}
      </body>
    </html>
  );
}
