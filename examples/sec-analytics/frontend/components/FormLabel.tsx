import type { FilingMeta } from "@/lib/types";

/** The form with a text label that says whether it is an original report or an amendment. */
export function FormLabel({ filing, showOriginal = false }: { filing: FilingMeta; showOriginal?: boolean }) {
  return (
    <span className="inline-flex flex-wrap items-center gap-1.5">
      <span className="font-semibold tabular-nums">{filing.form}</span>
      {filing.is_amendment ? (
        <span data-testid="amendment-label" className="tag border-warning! text-warning!">
          AMENDMENT
        </span>
      ) : showOriginal ? (
        <span data-testid="original-label" className="tag">
          ORIGINAL
        </span>
      ) : null}
    </span>
  );
}

/** "Source" on sec.gov: the exact document, in a new tab. */
export function SourceLink({ url, label = "Source" }: { url: string; label?: string }) {
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="[overflow-wrap:anywhere]">
      {label}
      <span aria-hidden="true" className="ml-0.5 text-[0.75em]">↗</span>
      <span className="sr-only"> (opens sec.gov in a new tab)</span>
    </a>
  );
}
