"use client";

import Link from "next/link";
import { type ReactNode, useCallback, useId } from "react";

import { Sparkline } from "@/components/Sparkline";
import { api } from "@/lib/api";
import { chartPoints, companyLine, findFigure, uniqueInOrder } from "@/lib/display";
import { formatMetric, unitCaption } from "@/lib/format";
import type { DataSourceChoice, DemoCompany } from "@/lib/types";
import { useApiResource } from "@/lib/useApiResource";

type CardProps = { company: DemoCompany; href: string; source: DataSourceChoice };

/**
 * One demo company on the home page. In Demo mode it shows ticker, name, CIK, exchange and a revenue sparkline from
 * the recorded data. In Live mode it loads nothing (no prefetching from SEC, folder rules §5): the figures appear when
 * the company is opened.
 */
export function DemoCompanyCard(props: CardProps) {
  return props.source === "live" ? <LiveCard {...props} /> : <RecordedCard {...props} />;
}

function CardFrame({ company, href, tag, chart, summary }: { company: DemoCompany; href: string; tag?: ReactNode; chart?: ReactNode; summary: ReactNode }) {
  const descriptionId = useId();
  return (
    <li className="min-w-0">
      <Link href={href} aria-label={companyLine(company)} aria-describedby={descriptionId} className="surface card-link flex h-full flex-col gap-3 p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-heading font-semibold tracking-tight">{company.ticker}</p>
            <p className="truncate text-fg">{company.name}</p>
          </div>
          {tag}
        </div>
        <p className="text-xs text-muted">
          CIK <span className="code-id">{company.cik}</span>
        </p>
        <div className="mt-auto flex flex-col gap-1">
          <div className="h-10">{chart}</div>
          <p id={descriptionId} className="text-xs text-muted">
            {summary}
          </p>
        </div>
      </Link>
    </li>
  );
}

function LiveCard({ company, href }: CardProps) {
  return <CardFrame company={company} href={href} summary={<span className="text-fg">Open the company to load its live figures.</span>} />;
}

function RecordedCard({ company, href, source }: CardProps) {
  // Two requests per card, both to existing endpoints on recorded data: the overview (sparkline and latest revenue)
  // and the profile (only for the exchange tag; if it fails, the tag is simply left out).
  const loadOverview = useCallback((signal: AbortSignal) => api.getOverview(company.cik, { signal }), [company.cik]);
  const loadProfile = useCallback((signal: AbortSignal) => api.getCompany(company.cik, { signal }), [company.cik]);
  const overview = useApiResource(`home-overview:${company.cik}:${source}`, loadOverview);
  const profile = useApiResource(`home-profile:${company.cik}:${source}`, loadProfile);

  const exchange = profile.status === "ok" ? uniqueInOrder(profile.data.exchanges).join(", ") : null;
  const points = overview.status === "ok" ? chartPoints(overview.data.chart) : [];
  const revenue = overview.status === "ok" ? findFigure(overview.data.key_figures, "revenue") : null;
  // The trend label names the first and last years that really have a revenue value.
  const withRevenue = points.filter((point) => point.revenue !== null);
  const first = withRevenue[0];
  const last = withRevenue[withRevenue.length - 1];

  let text: string;
  if (overview.status === "loading") text = "Loading revenue…";
  else if (overview.status === "error") text = "Revenue could not be loaded; open the company for details.";
  else if (revenue && revenue.status === "ok") text = `Revenue ${revenue.fiscal_year_label}: ${formatMetric(revenue)} ${unitCaption(revenue.unit)}`;
  else text = "No annual revenue reported.";

  return (
    <CardFrame
      company={company}
      href={href}
      tag={exchange ? <span className="tag shrink-0">{exchange}</span> : null}
      chart={withRevenue.length > 1 ? <Sparkline values={points.map((point) => point.revenue)} /> : overview.status === "loading" ? <span className="skeleton h-10! w-full" /> : null}
      summary={
        <>
          <span className="text-fg">{text}</span>
          {first && last && withRevenue.length > 1 ? (
            <span>
              {" "}
              · trend {first.label}–{last.label}
            </span>
          ) : null}
        </>
      }
    />
  );
}
