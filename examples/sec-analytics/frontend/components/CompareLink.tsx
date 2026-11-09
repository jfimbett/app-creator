"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useDataSource } from "@/lib/source";

/** The header's one navigation link (M4): the Compare screen, keeping the chosen data source. */
export function CompareLink() {
  const pathname = usePathname();
  const { href } = useDataSource();
  const current = pathname === "/compare";
  return (
    <Link
      href={href("/compare")}
      aria-current={current ? "page" : undefined}
      className={`shrink-0 text-table no-underline hover:no-underline ${current ? "border-b-2 border-accent text-fg" : "text-muted hover:text-fg"}`}
    >
      Compare
    </Link>
  );
}
