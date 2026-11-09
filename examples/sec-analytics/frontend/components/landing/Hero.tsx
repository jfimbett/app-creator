import Link from "next/link";

import { ThemedShot } from "@/components/landing/ThemedShot";
import { HEADLINE, SUBHEADLINE } from "@/lib/landing-content";

/** Hero (#top): headline, one sentence, two actions and a real screenshot of the app in the current theme. */
export function Hero() {
  return (
    <section id="top" aria-labelledby="hero-title" className="relative scroll-mt-16 overflow-hidden">
      <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-0 h-[520px]" style={{ background: "radial-gradient(60% 60% at 50% 0%, var(--hero-glow), transparent 70%)" }} />
      <div className="relative mx-auto max-w-6xl px-4 pb-16 pt-16 sm:px-6 md:pt-24">
        <div className="mx-auto max-w-3xl text-center">
          <p className="inline-flex items-center gap-2 rounded-full border border-line bg-panel px-3 py-1 text-xs text-muted">
            <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-positive" />
            Public SEC EDGAR data · Demo mode works offline
          </p>
          <h1 id="hero-title" className="mt-6 text-[2rem] font-semibold leading-tight tracking-tight text-fg sm:text-hero">
            {HEADLINE}
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-title text-muted">{SUBHEADLINE}</p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/app"
              className="rounded-md bg-accent px-5 py-2.5 text-title font-semibold text-on-accent no-underline shadow-card transition-opacity duration-[var(--dur-fast)] hover:no-underline hover:opacity-90"
            >
              Open the app
            </Link>
            <a
              href="#pricing"
              className="rounded-md border border-line-strong bg-panel px-5 py-2.5 text-title font-semibold text-fg no-underline transition-colors duration-[var(--dur-fast)] hover:bg-panel-raised hover:no-underline"
            >
              See pricing
            </a>
          </div>
        </div>

        <figure className="mx-auto mt-14 max-w-5xl">
          <div className="overflow-hidden rounded-lg border border-line bg-panel shadow-pop">
            <div aria-hidden="true" className="flex items-center gap-1.5 border-b border-line bg-panel-raised px-3 py-2">
              <span className="h-2.5 w-2.5 rounded-full bg-line-strong" />
              <span className="h-2.5 w-2.5 rounded-full bg-line-strong" />
              <span className="h-2.5 w-2.5 rounded-full bg-line-strong" />
            </div>
            <ThemedShot
              stem="app"
              eager
              width={1440}
              height={900}
              sizes="(min-width: 1024px) 1024px, 100vw"
              alt="The SEC Analytics company overview for Apple Inc. in Demo mode: profile, key figures and a ten-year revenue and net income chart from recorded SEC data."
            />
          </div>
          <figcaption className="mt-3 text-center text-xs text-muted">The real app in Demo mode, showing recorded SEC data.</figcaption>
        </figure>
      </div>
    </section>
  );
}
