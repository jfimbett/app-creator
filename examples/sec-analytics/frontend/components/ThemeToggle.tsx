"use client";

import { useCallback, useSyncExternalStore } from "react";

import { applyTheme, currentTheme, THEME_EVENT, type Theme, writeTheme } from "@/lib/theme";

function subscribe(onChange: () => void) {
  window.addEventListener(THEME_EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(THEME_EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

/** Server rendering assumes dark; the pre-paint script has already set the real theme on <html>. */
const serverTheme = (): Theme => "dark";

/**
 * One button that switches between the dark and light themes. It is an action, so it has no aria-pressed; its
 * name says what it will do ("Switch to light theme"). The choice is remembered in localStorage (display only).
 */
export function ThemeToggle({ className = "" }: { className?: string }) {
  const theme = useSyncExternalStore(subscribe, currentTheme, serverTheme);
  const next: Theme = theme === "dark" ? "light" : "dark";
  const label = `Switch to ${next} theme`;

  const toggle = useCallback(() => {
    applyTheme(next);
    writeTheme(next);
    window.dispatchEvent(new Event(THEME_EVENT));
  }, [next]);

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={label}
      title={label}
      data-testid="theme-toggle"
      data-theme-next={next}
      className={`inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-line-strong text-muted transition-colors duration-[var(--dur-fast)] hover:bg-panel-raised hover:text-fg ${className}`}
    >
      {theme === "dark" ? (
        // Sun: shown in dark mode, switches to light.
        <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
        </svg>
      ) : (
        // Moon: shown in light mode, switches to dark.
        <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      )}
      <span className="sr-only">{label}</span>
    </button>
  );
}
