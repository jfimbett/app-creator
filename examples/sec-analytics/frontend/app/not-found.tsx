import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { StatePanel } from "@/components/StatePanel";

/** Any address the app does not have. Rendered outside the route groups, so it brings the app shell itself. */
export default function NotFound() {
  return (
    <AppShell>
      <section aria-labelledby="not-found-title" className="flex max-w-2xl flex-col gap-3">
        <h1 id="not-found-title" className="text-heading font-semibold">
          Page not found
        </h1>
        <StatePanel
          kind="empty"
          title="There is no page at this address"
          message={
            <p>
              Search for a company with <kbd className="kbd">/</kbd>, or go back to the{" "}
              <Link href="/app">list of demo companies</Link>.
            </p>
          }
        />
      </section>
    </AppShell>
  );
}
