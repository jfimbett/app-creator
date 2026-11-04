// Pure helpers for the ?source= URL parameter. Demo is the default: anything else is treated as demo.

import type { DataSourceChoice } from "./types";

export function sourceFromParam(value: string | null | undefined): DataSourceChoice {
  return value === "live" ? "live" : "demo";
}

/** A path with the chosen source kept in its URL; demo needs no parameter. */
export function withSource(path: string, source: DataSourceChoice): string {
  return source === "live" ? `${path}?source=live` : path;
}
