"use client";

import { useEffect, useId, useRef, useState } from "react";

import { api, ApiError } from "@/lib/api";
import { activeDescendantId, CLOSED, comboboxKey, comboboxReducer, type ComboboxState, optionId } from "@/lib/combobox";
import { MAX_COMPANIES } from "@/lib/compare-state";
import { companyLine } from "@/lib/display";
import type { DataSourceChoice, SearchResult } from "@/lib/types";
import { SERIES_COLOURS } from "@/lib/compare-view";

const DEBOUNCE_MS = 120;

type Answer = { query: string; source: string; results: SearchResult[]; error: ApiError | null };

type Props = {
  ciks: readonly string[];
  /** Ticker and name per CIK when known (from search results or the last comparison). */
  names: Readonly<Record<string, { ticker: string; name: string }>>;
  source: DataSourceChoice;
  onAdd: (result: SearchResult) => void;
  onRemove: (cik: string) => void;
  /** "Compare 2–4 companies" or "Already in the comparison" after a refused add. */
  message: string | null;
  autoFocus: boolean;
};

/**
 * The companies being compared, as removable chips, and a search box that adds one. The search uses the same
 * backend search as the header: the demo universe in Demo, SEC's ticker file in Live.
 */
export function CompanyChips({ ciks, names, source, onAdd, onRemove, message, autoFocus }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const listboxId = useId();
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [combo, setCombo] = useState<ComboboxState>(CLOSED);
  const trimmed = query.trim();
  const current = answer && answer.query === trimmed && answer.source === source ? answer : null;
  const results = current?.results ?? [];
  const showPopup = combo.open && trimmed.length > 0;

  useEffect(() => {
    if (autoFocus) inputRef.current?.focus();
  }, [autoFocus]);

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
          setAnswer({ query: trimmed, source, results: [], error: error instanceof ApiError ? error : null });
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
    onAdd(result);
    inputRef.current?.focus();
  };

  const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    const outcome = comboboxKey(current ? combo : { ...combo, count: 0 }, event.key);
    if (!outcome.handled) return;
    event.preventDefault();
    setCombo(outcome.state);
    if (outcome.choose !== null && results[outcome.choose]) choose(results[outcome.choose]);
  };

  return (
    <div className="flex min-w-0 flex-col gap-1">
      <div className="flex flex-wrap items-center gap-1.5">
        <ul aria-label="Companies in the comparison" className="flex flex-wrap items-center gap-1.5">
          {ciks.map((cik, index) => {
            const known = names[cik];
            const label = known?.ticker || cik;
            return (
              <li key={cik} data-testid="company-chip" data-cik={cik} className="flex h-8 items-center gap-1.5 rounded-full border border-line-strong bg-panel-raised pl-3 pr-1 text-table">
                <span aria-hidden="true" className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: SERIES_COLOURS[index] }} />
                <span className="font-semibold">{label}</span>
                {known?.name ? <span className="hidden max-w-[12rem] truncate text-muted sm:inline">{known.name}</span> : null}
                <button
                  type="button"
                  aria-label={`Remove ${label}`}
                  onClick={() => onRemove(cik)}
                  className="inline-flex h-6 w-6 items-center justify-center rounded-full text-muted transition-colors duration-[var(--dur-fast)] hover:bg-panel hover:text-fg"
                >
                  ×
                </button>
              </li>
            );
          })}
        </ul>
        <div className="relative w-full min-w-0 sm:w-72">
          <label htmlFor={`${listboxId}-input`} className="sr-only">
            Add a company by name, ticker or CIK
          </label>
          <input
            ref={inputRef}
            id={`${listboxId}-input`}
            data-testid="compare-add"
            type="text"
            role="combobox"
            aria-autocomplete="list"
            aria-expanded={showPopup}
            aria-controls={listboxId}
            aria-activedescendant={showPopup ? activeDescendantId(combo, listboxId) : undefined}
            autoComplete="off"
            spellCheck={false}
            maxLength={100}
            placeholder={ciks.length >= MAX_COMPANIES ? "4 companies: remove one to add" : "Add company: name, ticker or CIK"}
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setCombo((state) => ({ ...state, open: event.target.value.trim().length > 0, activeIndex: -1 }));
            }}
            onBlur={() => setCombo((state) => comboboxReducer(state, { type: "close" }))}
            onKeyDown={onKeyDown}
            className="field h-8 w-full"
          />
          {showPopup ? (
            <div className="popover absolute left-0 right-0 top-[calc(100%+4px)] z-30 overflow-hidden">
              <ul id={listboxId} role="listbox" aria-label="Companies to add" className="max-h-64 overflow-y-auto py-1">
                {results.map((result, index) => (
                  <li
                    key={result.cik}
                    id={optionId(listboxId, index)}
                    role="option"
                    aria-selected={index === combo.activeIndex}
                    onMouseDown={(event) => event.preventDefault()}
                    onClick={() => choose(result)}
                    className={`cursor-pointer truncate border-l-2 px-2.5 py-1.5 ${index === combo.activeIndex ? "border-accent bg-panel" : "border-transparent hover:bg-panel"}`}
                  >
                    {companyLine(result)}
                  </li>
                ))}
              </ul>
              {!current ? <p className="px-2 pb-1.5 text-muted">Searching…</p> : null}
              {current?.error ? <p className="px-2 pb-1.5 text-negative">{current.error.message}</p> : null}
              {current && !current.error && results.length === 0 ? <p className="px-2 pb-1.5">No match</p> : null}
            </div>
          ) : null}
        </div>
      </div>
      <p role="status" aria-live="polite" data-testid="compare-message" className={message ? "text-table text-warning" : "sr-only"}>
        {message ?? ""}
      </p>
    </div>
  );
}
