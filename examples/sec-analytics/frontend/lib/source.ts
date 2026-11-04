"use client";

// Which data the person chose: recorded demo data or live SEC. It lives in the page URL (?source=live), so a
// reload keeps it and every screen reads the same value. The app never changes it by itself.

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useMemo } from "react";

import { sourceFromParam, withSource } from "./sourceParam";
import type { DataSourceChoice } from "./types";

export { sourceFromParam, withSource };

export function useDataSource() {
  const params = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const source = sourceFromParam(params.get("source"));

  const setSource = useCallback(
    (next: DataSourceChoice) => {
      const query = new URLSearchParams(params.toString());
      if (next === "live") query.set("source", "live");
      else query.delete("source");
      const text = query.toString();
      router.replace(text ? `${pathname}?${text}` : pathname, { scroll: false });
    },
    [params, pathname, router],
  );

  /** A link inside the app that keeps the chosen source. */
  const href = useCallback((path: string) => withSource(path, source), [source]);

  return useMemo(() => ({ source, setSource, href }), [source, setSource, href]);
}
