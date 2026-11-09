"use client";

import Link from "next/link";
import { useCallback, useId } from "react";

import { Sparkline } from "@/components/Sparkline";
import { api } from "@/lib/api";
import { chartPoints, companyLine, findFigure, uniqueInOrder } from "@/lib/display";
import { formatMetric, unitCaption } from "@/lib/format";
import type { DataSourceChoice, DemoCompany } from "@/lib/types";
import { useApiResource } from "@/lib/useApiResource";

const never = () => new Promise<never>(() => {});

/**
 * One demo company on the home page: ticker, name, CIK, exchange and a revenue sparkline, all from the existing
 * profile and overview endpoints. In Live the card does not load anything (no prefetching from SEC): the figures
 * appear when the company is opened.
 */
export function DemoCompanyCard({ company, href, source }: { company: DemoCompany; href: string; source: DataSourceChoice }) {
  const descriptionId = useId();
  const live = source === "live";
  const loadOverview = useCallback((signal: AbortSignal) => (live ? never() : api.getOverview(company.cik, { signal })), [company.cik, live]);
  const loadProfile = useCallback((signal: AbortSignal) => (live ? never() : api.getCompany(company.cik, { signal })), [company.cik, live]);
  const overview = useApiResource(`home-overview:${company.cik}:${source}`, loadOverview);
  const profile = useApiResource(`home-profile:${company.cik}:${source}`, loadProfile);

  const exchange = profile.status === "ok" ? uniqueInOrder(profile.data.exchanges).join(", ") : null;
  const points = overview.status === "ok" ? chartPoints(overview.data.chart) : [];
  const revenue = overview.status === "ok" ? findFigure(overview.data.key_figures, "revenue") : null;
  const first = points[0];
  const last = points[points.length - 1];

  let summary: string;
  if (live) summary = "Open the company to load its live figures.";
  else if (overview.status === "loading") summary = "Loading revenue…";
  else if (overview.status === "error") summary = "Revenue could not be loaded; open the company for details.";
  else if (revenue && revenue.status === "ok") summary = `Revenue ${revenue.fiscal_year_label}: ${formatMetric(revenue)} ${unitCaption(revenue.unit)}`;
  else summary = "No annual revenue reported.";

  return (
    <li className="min-w-0">
      <Link href={href} aria-label={companyLine(company)} aria-describedby={descriptionId} className="surface card-link flex h-full flex-col gap-3 p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-heading font-semibold tracking-tight">{company.ticker}</p>
            <p className="truncate text-fg">{company.name}</p>
          </div>
          {exchange ? <span className="tag shrink-0">{exchange}</span> : null}
        </div>
        <p className="text-xs text-muted">
          CIK <span className="code-id">{company.cik}</span>
        </p>
        <div className="mt-auto flex flex-col gap-1">
          <div className="h-10">
            {points.length > 1 ? <Sparkline values={points.map((point) => point.revenue)} /> : overview.status === "loading" && !live ? <span className="skeleton h-10! w-full" /> : null}
          </div>
          <p id={descriptionId} className="text-xs text-muted">
            <span className="text-fg">{summary}</span>
            {first && last && points.length > 1 ? (
              <span>
                {" "}
                · trend {first.label}–{last.label}
              </span>
            ) : null}
          </p>
        </div>
      </Link>
    </li>
  );
}
