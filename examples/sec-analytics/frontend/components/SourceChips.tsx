"use client";

import Link from "next/link";

import { linkWithSource } from "@/lib/ai";
import { useDataSource } from "@/lib/source";
import type { AiCitation } from "@/lib/types";

/**
 * The sources an answer cited, checked by the backend against what it supplied: `[F2] Net income · FY2026 …`.
 * A fact chip opens the company's Overview; a passage chip opens the reader at that block. A chip shows that the
 * source exists and was supplied, not that the sentence citing it is true. A link that is not an app-internal path
 * is never followed: that chip is plain text.
 */
export function SourceChips({ citations }: { citations: readonly AiCitation[] }) {
  const { source } = useDataSource();
  const valid = citations.filter((citation) => citation.valid);
  if (valid.length === 0) return null;
  return (
    <ul aria-label="Cited sources" data-testid="source-chips" className="flex flex-wrap gap-1.5">
      {valid.map((citation) => {
        const tip = `${citation.period}${citation.date ? ` · filed ${citation.date}` : ""}`;
        const href = linkWithSource(citation.link, source);
        const common = {
          title: tip,
          "aria-label": `${citation.source_id}: ${citation.label}, ${tip}`,
          "data-testid": "source-chip",
          "data-kind": citation.kind,
          "data-source-id": citation.source_id,
          className: `inline-flex max-w-full items-baseline gap-1 rounded-md border border-line-strong bg-panel-raised px-1.5 py-0.5 text-table text-fg no-underline ${href ? "hover:border-link hover:no-underline" : ""}`,
        };
        const content = (
          <>
            <span className="code-id shrink-0 text-accent">[{citation.source_id}]</span>
            <span className="min-w-0 [overflow-wrap:anywhere]">{citation.label}</span>
          </>
        );
        return (
          <li key={citation.source_id} className="min-w-0 max-w-full">
            {href ? (
              <Link href={href} {...common}>
                {content}
              </Link>
            ) : (
              <span {...common}>{content}</span>
            )}
          </li>
        );
      })}
    </ul>
  );
}
