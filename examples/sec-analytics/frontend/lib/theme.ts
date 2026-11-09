// The colour theme: a display preference only. It is the app's one localStorage entry, under
// "sec-analytics.theme", with the value "dark" or "light". It never holds the AI key or anything about it.
// Dark is the default; any missing, invalid or unreadable value means dark.

export type Theme = "dark" | "light";

export const THEME_STORAGE_KEY = "sec-analytics.theme";

/** Fired on window when the theme changes, so every toggle on the page shows the same state. */
export const THEME_EVENT = "sec-analytics:theme";

/** The stored theme, or "dark" when nothing valid is stored or storage cannot be read. */
export function readTheme(): Theme {
  try {
    return window.localStorage.getItem(THEME_STORAGE_KEY) === "light" ? "light" : "dark";
  } catch {
    return "dark";
  }
}

/** Remembers the choice. A blocked storage is ignored: the theme still applies for this page. */
export function writeTheme(theme: Theme): void {
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    // Storage disabled (private mode, policy): keep going without remembering.
  }
}

/** Shows the theme by setting <html data-theme="…">; globals.css picks the colours from it. */
export function applyTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
}

/** The theme currently shown on the page (set before first paint by THEME_INIT_SCRIPT). */
export function currentTheme(): Theme {
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

/**
 * The same rule as readTheme, as a tiny script for the root layout's <head>. It runs before the first paint, so a
 * light-theme visitor never sees a dark flash. It is a fixed string (no user data) and on any error leaves dark.
 */
export const THEME_INIT_SCRIPT = `(function(){var t="dark";try{if(window.localStorage.getItem(${JSON.stringify(
  THEME_STORAGE_KEY,
)})==="light")t="light"}catch(e){}document.documentElement.dataset.theme=t})();`;
