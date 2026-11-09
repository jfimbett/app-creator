"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";

import { api, ApiError } from "@/lib/api";
import { activeDescendantId, CLOSED, comboboxKey, comboboxReducer, type ComboboxState, optionId } from "@/lib/combobox";
import { companyLine } from "@/lib/display";
import { isFocusSearchShortcut } from "@/lib/shortcuts";
import { useDataSource } from "@/lib/source";
import type { SearchResult } from "@/lib/types";

export const UNIVERSE_NOTE = "Search covers the demo companies only: Apple, Microsoft, Alphabet";
export const NO_MATCH = "No match in the demo universe (3 companies)";
export const LIVE_UNIVERSE_NOTE = "Live search covers SEC filers listed in the SEC ticker file; other filers can be opened by CIK.";
export const LIVE_NO_MATCH = "No match in the SEC ticker file";
const QUERY_MAX = 100;
const DEBOUNCE_MS = 120;

type Answer = { query: string; source: string; results: SearchResult[]; error: ApiError | null };

/**
 * The header search: an accessible combobox over the demo universe or, in Live, SEC's ticker file.
 * "/" or Ctrl/Cmd-K focus it; ↑/↓ move, Enter opens the highlighted company, Esc closes the list.
 * On the home page the demo-universe note is always visible under the box.
 */
/** The pages whose own hero holds the company search; the header leaves its search out there (one search per page). */
export const SEARCH_IN_PAGE = new Set(["/app"]);

/** `size="hero"`: the large search of the home page; the default is the compact header search. */
export function CompanySearch({ size = "header" }: { size?: "header" | "hero" }) {
  const hero = size === "hero";
  const router = useRouter();
  const pathname = usePathname();
  const { source, href } = useDataSource();
  const universeNote = source === "live" ? LIVE_UNIVERSE_NOTE : UNIVERSE_NOTE;
  const noMatch = source === "live" ? LIVE_NO_MATCH : NO_MATCH;
  const inputRef = useRef<HTMLInputElement>(null);
  const listboxId = useId();
  const noteId = useId();
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [combo, setCombo] = useState<ComboboxState>(CLOSED);

  const trimmed = query.trim();
  const current = answer && answer.query === trimmed && answer.source === source ? answer : null;
  const results = current?.results ?? [];
  const showPopup = combo.open && trimmed.length > 0;

  // Global shortcuts: "/" and Ctrl/Cmd-K move focus here (ignored while typing in another field).
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (!isFocusSearchShortcut(event, inputRef.current)) return;
      event.preventDefault();
      inputRef.current?.focus();
      inputRef.current?.select();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

  // Ask the backend shortly after typing stops; an older request is cancelled by a newer one.
  useEffect(() => {
    if (!trimmed) return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      api.searchCompanies(trimmed, { signal: controller.signal, source }).then(
        (response) => {
          setAnswer({ query: trimmed, source, results: response.results, error: null });
          setCombo((state) => comboboxReducer(state, { type: "results", count: response.results.length }));
        },
        (error: unknown) => {
          if (controller.signal.aborted) return;
          const apiError = error instanceof ApiError ? error : null;
          setAnswer({ query: trimmed, source, results: [], error: apiError });
          setCombo((state) => comboboxReducer(state, { type: "results", count: 0 }));
        },
      );
    }, DEBOUNCE_MS);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [trimmed, source]);

  const choose = (result: SearchResult) => {
    setCombo(CLOSED);
    setQuery("");
    setAnswer(null);
    inputRef.current?.blur();
    router.push(href(`/companies/${result.cik}`));
  };

  const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    const outcome = comboboxKey(current ? combo : { ...combo, count: 0 }, event.key);
    if (!outcome.handled) return;
    event.preventDefault();
    setCombo(outcome.state);
    if (outcome.choose !== null && results[outcome.choose]) choose(results[outcome.choose]);
  };

  const announcement = !trimmed || !current
    ? ""
    : current.error
      ? current.error.message
      : results.length === 0
        ? noMatch
        : `${results.length} ${results.length === 1 ? "company" : "companies"} found`;

  return (
    <div>
      <label htmlFor={`${listboxId}-input`} className="sr-only">
        Search companies by name, ticker or CIK
      </label>
      <div className="relative">
        <div className={`field flex items-center gap-2 py-0! ${hero ? "min-h-12 rounded-lg! px-3!" : "min-h-8 px-2!"}`}>
          <svg aria-hidden="true" width={hero ? 18 : 14} height={hero ? 18 : 14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="shrink-0 text-muted">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
          <input
            ref={inputRef}
            id={`${listboxId}-input`}
            type="text"
            role="combobox"
            aria-autocomplete="list"
            aria-expanded={showPopup}
            aria-controls={listboxId}
            aria-activedescendant={showPopup ? activeDescendantId(combo, listboxId) : undefined}
            aria-describedby={noteId}
            autoComplete="off"
            spellCheck={false}
            maxLength={QUERY_MAX}
            placeholder="Search name, ticker or CIK"
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setCombo((state) => ({ ...state, open: event.target.value.trim().length > 0, activeIndex: -1 }));
            }}
            onFocus={() => trimmed && current && setCombo((state) => comboboxReducer(state, { type: "results", count: results.length }))}
            onBlur={() => setCombo((state) => comboboxReducer(state, { type: "close" }))}
            onKeyDown={onKeyDown}
            className={`min-w-0 flex-1 bg-transparent py-1 text-fg placeholder:text-muted focus:outline-none ${hero ? "text-title" : ""}`}
          />
          <kbd aria-hidden="true" className="kbd text-muted">
            /
          </kbd>
        </div>

        {showPopup ? (
          <div className="popover absolute left-0 right-0 top-[calc(100%+4px)] z-30 overflow-hidden">
            <ul id={listboxId} role="listbox" aria-label="Matching companies" className="max-h-72 overflow-y-auto py-1">
              {results.map((result, index) => {
                const active = index === combo.activeIndex;
                return (
                  <li
                    key={result.cik}
                    id={optionId(listboxId, index)}
                    role="option"
                    aria-selected={active}
                    onMouseDown={(event) => event.preventDefault()}
                    onClick={() => choose(result)}
                    className={`flex cursor-pointer items-baseline justify-between gap-3 border-l-2 px-2 py-1 ${active ? "border-accent bg-panel text-fg" : "border-transparent text-fg hover:bg-panel"}`}
                  >
                    <span className="min-w-0 truncate">{companyLine(result)}</span>
                    <span className="label-caps shrink-0 text-muted">by {result.match}</span>
                  </li>
                );
              })}
            </ul>
            {!current ? (
              <p className="px-2 pb-1.5 text-muted">Searching…</p>
            ) : current.error ? (
              <p className="px-2 pb-1.5 text-negative">{current.error.message}</p>
            ) : results.length === 0 ? (
              <p className="px-2 pb-1.5 text-fg">{noMatch}</p>
            ) : null}
            <p className="border-t border-line px-2 py-1 text-label text-muted">{universeNote}</p>
          </div>
        ) : null}
      </div>
      <p id={noteId} className={SEARCH_IN_PAGE.has(pathname) ? "mt-2 text-table text-muted" : "sr-only"} data-testid="universe-note">
        {universeNote}
      </p>
      <p role="status" aria-live="polite" className="sr-only">
        {announcement}
      </p>
    </div>
  );
}
