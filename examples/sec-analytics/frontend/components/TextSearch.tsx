"use client";

import { countLabel, MIN_QUERY_LENGTH, normalizeQuery, type SearchResult } from "@/lib/text-search";

type Props = {
  query: string;
  onQuery: (value: string) => void;
  result: SearchResult;
  current: number;
  pending: boolean;
  onStep: (direction: 1 | -1) => void;
  onClear: () => void;
};

const BUTTON = "btn";

/** The sticky search bar of the reader: Enter for next, Shift+Enter for previous, Esc to clear. */
export function TextSearch({ query, onQuery, result, current, pending, onStep, onClear }: Props) {
  const typed = normalizeQuery(query);
  const tooShort = typed.length > 0 && typed.length < MIN_QUERY_LENGTH;
  const hasMatches = result.matches.length > 0;
  return (
    <div role="search" className="sticky top-0 z-10 flex flex-wrap items-center gap-2 rounded-t-[7px] border-b border-line bg-panel-raised px-4 py-2 text-table md:top-14">
      <label htmlFor="filing-search" className="label-caps text-muted">
        Search this filing
      </label>
      <input
        id="filing-search"
        data-testid="filing-search"
        type="search"
        value={query}
        onChange={(event) => onQuery(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            if (hasMatches) onStep(event.shiftKey ? -1 : 1);
          } else if (event.key === "Escape") {
            onClear();
          }
        }}
        placeholder="For example: revenue"
        className="field min-w-0 flex-1 basis-40"
      />
      <span data-testid="search-count" aria-live="polite" className="min-w-[5.5rem] tabular-nums text-muted">
        {typed.length === 0 ? "" : tooShort ? "Type 2 or more characters" : pending ? "Searching…" : countLabel(result, current)}
      </span>
      <span className="flex gap-1">
        <button type="button" data-testid="search-previous" aria-label="Previous match" className={BUTTON} disabled={!hasMatches} onClick={() => onStep(-1)}>
          ↑
        </button>
        <button type="button" data-testid="search-next" aria-label="Next match" className={BUTTON} disabled={!hasMatches} onClick={() => onStep(1)}>
          ↓
        </button>
        <button type="button" data-testid="search-clear" className={BUTTON} disabled={query.length === 0} onClick={onClear}>
          Clear
        </button>
      </span>
    </div>
  );
}
