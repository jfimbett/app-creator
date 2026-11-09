"use client";

import Link from "next/link";

import { StatePanel } from "@/components/StatePanel";

/** Shown when a screen fails while rendering. No stack trace; the digest lets a developer find the log entry. */
export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <section aria-labelledby="error-title" className="flex max-w-2xl flex-col gap-3">
      <h1 id="error-title" className="text-heading font-semibold">
        This page could not be shown
      </h1>
      <StatePanel
        kind="error"
        title="Something went wrong while showing this page"
        message={
          <p>
            Try again. If it keeps happening, go back to the <Link href="/app">list of demo companies</Link>.
          </p>
        }
        reference={error.digest ?? null}
        action={{ label: "Try again", onClick: reset }}
      />
    </section>
  );
}
