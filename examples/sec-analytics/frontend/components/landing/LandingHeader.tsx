"use client";

import Link from "next/link";
import { useEffect, useId, useRef, useState } from "react";

import { BrandMark } from "@/components/BrandMark";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LANDING_NAV } from "@/lib/landing-content";

/**
 * Landing header: brand, anchor links to the page's sections, the theme toggle and "Open the app".
 * Below the md breakpoint the anchor links fold into a menu button; Esc or choosing a link closes it, and Esc
 * returns focus to the button.
 */
export function LandingHeader() {
  const [open, setOpen] = useState(false);
  const menuId = useId();
  const buttonRef = useRef<HTMLButtonElement>(null);
  const headerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
        buttonRef.current?.focus();
      }
    };
    // A click or focus outside the header closes the menu too.
    const onOutside = (event: Event) => {
      if (headerRef.current && event.target instanceof Node && !headerRef.current.contains(event.target)) setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onOutside);
    document.addEventListener("focusin", onOutside);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onOutside);
      document.removeEventListener("focusin", onOutside);
    };
  }, [open]);

  return (
    <header ref={headerRef} className="sticky top-0 z-20 border-b border-line bg-bg/85 backdrop-blur supports-[backdrop-filter]:bg-bg/75">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2 text-fg no-underline hover:no-underline" aria-label="SEC Analytics, top of the page">
          <BrandMark />
          <span className="text-title font-semibold tracking-tight">SEC Analytics</span>
        </Link>

        <nav aria-label="Sections" className="ml-4 hidden md:block">
          <ul className="flex items-center gap-1">
            {LANDING_NAV.map((item) => (
              <li key={item.href}>
                <a href={item.href} className="rounded-md px-3 py-1.5 text-muted no-underline transition-colors duration-[var(--dur-fast)] hover:bg-panel-raised hover:text-fg hover:no-underline">
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <ThemeToggle />
          <Link
            href="/app"
            className="hidden rounded-md bg-accent px-3.5 py-1.5 font-semibold text-on-accent no-underline shadow-card transition-opacity duration-[var(--dur-fast)] hover:no-underline hover:opacity-90 sm:inline-block"
          >
            Open the app
          </Link>
          <button
            ref={buttonRef}
            type="button"
            className="inline-flex h-8 items-center gap-1.5 rounded-md border border-line-strong px-2.5 text-fg md:hidden"
            aria-expanded={open}
            aria-controls={menuId}
            onClick={() => setOpen((value) => !value)}
            data-testid="landing-menu-button"
          >
            <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
            </svg>
            Menu
          </button>
        </div>
      </div>

      <nav id={menuId} aria-label="Sections" hidden={!open} className="border-t border-line bg-panel md:hidden" data-testid="landing-menu">
        <ul className="mx-auto flex max-w-6xl flex-col px-4 py-2">
          {LANDING_NAV.map((item) => (
            <li key={item.href}>
              <a href={item.href} onClick={() => setOpen(false)} className="block rounded-md px-2 py-2.5 text-fg no-underline hover:bg-panel-raised hover:no-underline">
                {item.label}
              </a>
            </li>
          ))}
          <li className="mt-1 border-t border-line pt-2">
            <Link href="/app" className="block rounded-md px-2 py-2.5 font-semibold text-accent no-underline hover:bg-panel-raised hover:no-underline">
              Open the app
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  );
}
