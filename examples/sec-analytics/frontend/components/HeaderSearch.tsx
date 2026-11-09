"use client";

import { usePathname } from "next/navigation";

import { CompanySearch, SEARCH_IN_PAGE } from "@/components/CompanySearch";

/** The header search on every app screen except the home page, where the search is the hero's main control. */
export function HeaderSearch() {
  const pathname = usePathname();
  if (SEARCH_IN_PAGE.has(pathname)) return null;
  return (
    <div data-testid="header-search-slot" className="order-last w-full min-w-0 md:order-none md:w-auto md:max-w-xl md:flex-1">
      <CompanySearch />
    </div>
  );
}
