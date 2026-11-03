import Link from "next/link";

import { StatePanel } from "@/components/StatePanel";

/** Any address the app does not have. */
export default function NotFound() {
  return (
    <section aria-labelledby="not-found-title" className="flex max-w-2xl flex-col gap-3">
      <h1 id="not-found-title" className="text-heading font-semibold">
        Page not found
      </h1>
      <StatePanel
        kind="empty"
        title="There is no page at this address"
        message={
          <p>
            Search for a company with <kbd className="rounded-sm border border-line px-1">/</kbd>, or go back to the{" "}
            <Link href="/">list of demo companies</Link>.
          </p>
        }
      />
    </section>
  );
}
