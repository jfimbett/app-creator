"use client";

import { type CSSProperties, type ReactNode, useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { formatDate, formatExactMetric, formatFiscalYear, formatPeriod, UNAVAILABLE } from "@/lib/format";
import type { MetricValue } from "@/lib/types";

const TIP_WIDTH = 320;
const EDGE = 8;
const CLOSE_DELAY_MS = 120;

function placement(rect: DOMRect): CSSProperties {
  const width = Math.min(TIP_WIDTH, window.innerWidth - 2 * EDGE);
  const left = Math.min(Math.max(EDGE, rect.left), window.innerWidth - width - EDGE);
  const below = window.innerHeight - rect.bottom;
  // Open toward the side with more room, so a long list of inputs stays on screen.
  return below >= rect.top
    ? { top: rect.bottom + 4, left, width, maxHeight: below - EDGE - 4 }
    : { bottom: window.innerHeight - rect.top + 4, left, width, maxHeight: rect.top - EDGE - 4 };
}

function ReportedDetails({ metric }: { metric: MetricValue }) {
  const p = metric.provenance;
  if (!p) return <p className="mt-1">No SEC fact for this period{metric.reason ? `: ${metric.reason}` : ""}.</p>;
  return (
    <dl className="mt-1 grid grid-cols-[auto_1fr] gap-x-3">
      <dt className="text-muted">Value</dt>
      <dd className="num text-left">{formatExactMetric(metric)}</dd>
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
      <dt className="text-muted">Source</dt>
      <dd>
        <a href={p.source_url} target="_blank" rel="noreferrer">
          SEC Company Facts
        </a>
      </dd>
    </dl>
  );
}

function inputValue(input: MetricValue): string {
  if (input.status === "ok") return formatExactMetric(input);
  if (input.status === "not_meaningful") return input.reason || "n/m";
  return input.status === "missing" ? "MISSING" : UNAVAILABLE;
}

function DerivedDetails({ metric }: { metric: MetricValue }) {
  return (
    <>
      <dl className="mt-1 grid grid-cols-[auto_1fr] gap-x-3">
        <dt className="text-muted">Value</dt>
        <dd className="num text-left">{metric.status === "ok" ? formatExactMetric(metric) : inputValue(metric)}</dd>
        {metric.reason ? (
          <>
            <dt className="text-muted">Reason</dt>
            <dd>{metric.reason}</dd>
          </>
        ) : null}
        <dt className="text-muted">Formula</dt>
        <dd>{metric.formula}</dd>
        {metric.note ? (
          <>
            <dt className="text-muted">Note</dt>
            <dd>{metric.note}</dd>
          </>
        ) : null}
      </dl>
      <p className="label-caps mt-2 text-muted">Inputs</p>
      <ul className="mt-0.5">
        {metric.inputs.map((input) => (
          <li key={`${input.metric_id}-${input.period_end}`} className="flex flex-wrap justify-between gap-x-3">
            <span className="code-id">{input.metric_id}</span>
            <span className="num">
              {inputValue(input)} · {formatFiscalYear(input.fiscal_year_label, input.period_end)}
            </span>
          </li>
        ))}
      </ul>
    </>
  );
}

/**
 * Wraps a shown value so hovering or focusing it opens where it came from. A reported value lists its SEC fact and a
 * link; a derived value lists its formula, its inputs and any reason it is not shown. The tip stays open while the
 * pointer is on it (so its link can be clicked), stays inside the viewport at 390 px, and is rendered into <body> so
 * a scrolling table cannot clip it.
 */
export function ProvenanceTip({ metric, children, className }: { metric: MetricValue; children: ReactNode; className?: string }) {
  const tipId = useId();
  const triggerRef = useRef<HTMLButtonElement>(null);
  const closeTimer = useRef<number | undefined>(undefined);
  const [style, setStyle] = useState<CSSProperties | null>(null);

  const cancelClose = () => window.clearTimeout(closeTimer.current);
  const open = () => {
    cancelClose();
    const rect = triggerRef.current?.getBoundingClientRect();
    if (rect) setStyle(placement(rect));
  };
  const close = () => {
    cancelClose();
    setStyle(null);
  };
  const closeSoon = () => {
    cancelClose();
    closeTimer.current = window.setTimeout(() => setStyle(null), CLOSE_DELAY_MS);
  };

  useEffect(() => cancelClose, []);

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        aria-describedby={style ? tipId : undefined}
        onMouseEnter={open}
        onMouseLeave={closeSoon}
        onFocus={open}
        onBlur={closeSoon}
        onClick={() => (style ? close() : open())}
        onKeyDown={(event) => {
          if (event.key === "Escape") close();
        }}
        className={`cursor-help rounded-sm border-b border-dotted border-muted text-inherit ${className ?? ""}`}
      >
        {children}
      </button>
      {style
        ? createPortal(
            <div
              id={tipId}
              role="tooltip"
              data-testid="provenance-tip"
              style={style}
              onMouseEnter={cancelClose}
              onMouseLeave={closeSoon}
              className="popover fixed z-40 overflow-y-auto p-2.5 text-left text-table leading-5"
            >
              <p className="label-caps text-muted">
                {metric.kind === "derived" ? "Calculated value" : "Source of this value"} · {formatFiscalYear(metric.fiscal_year_label, metric.period_end)}
              </p>
              {metric.kind === "derived" ? <DerivedDetails metric={metric} /> : <ReportedDetails metric={metric} />}
            </div>,
            document.body,
          )
        : null}
    </>
  );
}
