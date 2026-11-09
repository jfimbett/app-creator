"use client";

import { type ReactNode, useRef, useState } from "react";

import { AnalystPanel } from "@/components/AnalystPanel";
import type { AiScope } from "@/lib/types";

type Props = {
  /** The page's <h1>; the Analyst button sits at the right of it, in the page toolbar. */
  heading: ReactNode;
  /** What the analyst may use on this page, or null when there is nothing to analyse yet (no button). */
  scope: AiScope | null;
  children: ReactNode;
};

/**
 * A page with the optional analyst (M5): the page content and, once opened, the analyst panel. From 1280 px the
 * panel sits next to the content and pushes it narrower; below that it is a full-screen sheet with a close button.
 */
export function AnalystLayout({ heading, scope, children }: Props) {
  const [open, setOpen] = useState(false);
  const button = useRef<HTMLButtonElement>(null);
  const showPanel = open && scope !== null;

  const close = () => {
    setOpen(false);
    button.current?.focus();
  };

  return (
    <div className="flex items-start gap-4">
      {/* @container: the page lays itself out by the width it gets, which shrinks when the analyst panel opens. */}
      <div className="@container flex min-w-0 flex-1 flex-col gap-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          {heading}
          {scope ? (
            <button
              ref={button}
              type="button"
              data-testid="analyst-open"
              aria-expanded={showPanel}
              aria-controls={showPanel ? "analyst-panel" : undefined}
              onClick={() => setOpen((current) => !current)}
              className={`btn min-h-8! px-3! font-semibold ${showPanel ? "btn-primary" : "border-accent!"}`}
            >
              Analyst
            </button>
          ) : null}
        </div>
        {children}
      </div>
      {showPanel ? <AnalystPanel scope={scope} onClose={close} /> : null}
    </div>
  );
}
