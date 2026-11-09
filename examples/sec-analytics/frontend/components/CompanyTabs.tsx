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
    <nav aria-label="Company views" className="flex gap-1 border-b border-line text-base">
      {tabs.map((tab) => (
        <Link
          key={tab.id}
          href={href(tab.path)}
          aria-current={active === tab.id ? "page" : undefined}
          className={`-mb-px border-b-2 px-3 py-2 no-underline transition-colors duration-[var(--dur-fast)] hover:no-underline ${active === tab.id ? "border-accent font-semibold text-fg" : "border-transparent text-muted hover:border-line-strong hover:text-fg"}`}
        >
          {tab.label}
        </Link>
      ))}
    </nav>
  );
}
