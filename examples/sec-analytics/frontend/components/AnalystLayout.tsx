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
    <div className="flex items-start gap-3">
      <div className="flex min-w-0 flex-1 flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          {heading}
          {scope ? (
            <button
              ref={button}
              type="button"
              data-testid="analyst-open"
              aria-expanded={showPanel}
              aria-controls={showPanel ? "analyst-panel" : undefined}
              onClick={() => setOpen((current) => !current)}
              className={`rounded-sm border px-2.5 py-0.5 text-table font-semibold ${showPanel ? "border-accent bg-accent text-on-accent" : "border-accent text-fg hover:bg-accent hover:text-on-accent"}`}
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
