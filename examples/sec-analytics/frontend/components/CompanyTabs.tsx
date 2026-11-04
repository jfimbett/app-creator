"use client";

import Link from "next/link";

import { useDataSource } from "@/lib/source";

type Props = { cik: string; active: "overview" | "filings" };

/** The company's two views. Plain links, so each view has its own address and keeps the chosen source. */
export function CompanyTabs({ cik, active }: Props) {
  const { href } = useDataSource();
  const tabs = [
    { id: "overview", label: "Overview", path: `/companies/${cik}` },
    { id: "filings", label: "Filings", path: `/companies/${cik}/filings` },
  ] as const;
  return (
    <nav aria-label="Company views" className="flex gap-4 border-b border-line text-table">
      {tabs.map((tab) => (
        <Link
          key={tab.id}
          href={href(tab.path)}
          aria-current={active === tab.id ? "page" : undefined}
          className={`-mb-px border-b-2 px-1 py-1 ${active === tab.id ? "border-accent font-semibold text-fg" : "border-transparent text-muted hover:text-fg"}`}
        >
          {tab.label}
        </Link>
      ))}
    </nav>
  );
}
