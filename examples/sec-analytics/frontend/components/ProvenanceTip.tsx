"use client";

import { type ReactNode, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { formatDate, formatExact, formatPeriod } from "@/lib/format";
import type { MetricValue } from "@/lib/types";

const TIP_WIDTH = 304;
const EDGE = 8;

type Position = { top: number; left: number };

/**
 * Wraps a shown value so hovering or focusing it opens where the value came from: concept, taxonomy, unit,
 * period, form, accession and filing date, plus the exact value. The tip uses fixed positioning so it is not
 * clipped by a scrolling table, and it stays inside the viewport at 390 px. It is rendered into <body> (a portal),
 * so a value inside a paragraph or table cell never contains block elements.
 */
export function ProvenanceTip({ metric, children, className }: { metric: MetricValue; children: ReactNode; className?: string }) {
  const tipId = useId();
  const triggerRef = useRef<HTMLButtonElement>(null);
  const [position, setPosition] = useState<Position | null>(null);

  const open = () => {
    const rect = triggerRef.current?.getBoundingClientRect();
    if (!rect) return;
    const width = Math.min(TIP_WIDTH, window.innerWidth - 2 * EDGE);
    const left = Math.min(Math.max(EDGE, rect.left), window.innerWidth - width - EDGE);
    setPosition({ top: rect.bottom + 4, left });
  };
  const close = () => setPosition(null);

  const p = metric.provenance;

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        aria-describedby={position ? tipId : undefined}
        onMouseEnter={open}
        onMouseLeave={close}
        onFocus={open}
        onBlur={close}
        onClick={() => (position ? close() : open())}
        onKeyDown={(event) => {
          if (event.key === "Escape") close();
        }}
        className={`cursor-help rounded-sm border-b border-dotted border-muted text-inherit ${className ?? ""}`}
      >
        {children}
      </button>
      {position
        ? createPortal(
            <div
              id={tipId}
              role="tooltip"
              data-testid="provenance-tip"
              style={{ top: position.top, left: position.left, width: Math.min(TIP_WIDTH, window.innerWidth - 2 * EDGE) }}
              className="fixed z-40 border border-line bg-panel-raised p-2 text-left text-table leading-5 text-fg shadow-lg shadow-black/40"
            >
              <p className="label-caps text-muted">Source of this value</p>
              {p ? (
                <dl className="mt-1 grid grid-cols-[auto_1fr] gap-x-3">
                  <dt className="text-muted">Value</dt>
                  <dd className="num text-left">{formatExact(metric.value, metric.unit)}</dd>
                  <dt className="text-muted">Concept</dt>
                  <dd className="code-id [overflow-wrap:anywhere]">{p.concept}</dd>
                  <dt className="text-muted">Taxonomy</dt>
                  <dd className="code-id">{p.taxonomy}</dd>
                  <dt className="text-muted">Unit</dt>
                  <dd className="code-id">{p.unit}</dd>
                  <dt className="text-muted">Period</dt>
                  <dd className="num text-left">{formatPeriod(p.start, p.end)}</dd>
                  <dt className="text-muted">Form</dt>
                  <dd className="code-id">{p.form}</dd>
                  <dt className="text-muted">Accession</dt>
                  <dd className="code-id">{p.accession}</dd>
                  <dt className="text-muted">Filed</dt>
                  <dd className="num text-left">{formatDate(p.filed)}</dd>
                </dl>
              ) : (
                <p className="mt-1">No SEC fact for this period{metric.reason ? `: ${metric.reason}` : ""}.</p>
              )}
            </div>,
            document.body,
          )
        : null}
    </>
  );
}
