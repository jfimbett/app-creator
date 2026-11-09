"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useDataSource } from "@/lib/source";

const ITEMS = [
  { label: "Home", path: "/app" },
  { label: "Compare", path: "/compare" },
] as const;

/** The header's primary navigation: Home (/app) and Compare, each keeping the chosen data source. */
export function MainNav() {
  const pathname = usePathname();
  const { href } = useDataSource();
  return (
    <ul className="flex items-center gap-1">
      {ITEMS.map((item) => {
        const current = pathname === item.path;
        return (
          <li key={item.path}>
            <Link
              href={href(item.path)}
              aria-current={current ? "page" : undefined}
              className={`inline-flex h-8 items-center rounded-md px-2.5 text-table no-underline transition-colors duration-[var(--dur-fast)] hover:bg-panel-raised hover:text-fg hover:no-underline ${current ? "bg-panel-raised font-semibold text-fg shadow-[inset_0_-2px_0_var(--accent)]" : "text-muted"}`}
            >
              {item.label}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
