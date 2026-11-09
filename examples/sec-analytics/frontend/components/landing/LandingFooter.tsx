import Link from "next/link";

import { BrandMark } from "@/components/BrandMark";
import { DISCLAIMER, REPO_URL } from "@/lib/landing-content";

/** Final call to action, the last section inside <main>. */
export function FinalCta() {
  return (
    <section aria-labelledby="cta-title" className="mx-auto max-w-6xl px-4 py-16 sm:px-6 md:py-24">
      <div className="rounded-lg border border-line bg-panel px-6 py-12 text-center shadow-pop" style={{ backgroundImage: "radial-gradient(70% 120% at 50% 0%, var(--hero-glow), transparent 70%)" }}>
        <h2 id="cta-title" className="text-display font-semibold tracking-tight text-fg">
          Open a company and follow the numbers
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-title text-muted">No sign-up. The figures, filings and comparisons need no key, and Demo mode works offline.</p>
        <Link
          href="/app"
          className="mt-8 inline-block rounded-md bg-accent px-6 py-3 text-title font-semibold text-on-accent no-underline shadow-card hover:no-underline hover:opacity-90"
        >
          Open the app
        </Link>
      </div>
    </section>
  );
}

/** The footer: app links, the repository, the disclaimer (O5) and the fictional copyright. */
export function LandingFooter() {
  return (
    <footer className="border-t border-line bg-panel">
      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 sm:px-6 md:grid-cols-[2fr_1fr_1fr]">
        <div>
          <p className="flex items-center gap-2 font-semibold text-fg">
            <BrandMark size={20} /> SEC Analytics
          </p>
          <p className="mt-3 max-w-md text-xs text-muted" data-testid="landing-disclaimer">
            {DISCLAIMER}
          </p>
        </div>
        <nav aria-label="The app">
          <h2 className="label-caps text-muted">The app</h2>
          <ul className="mt-3 flex flex-col gap-1.5">
            <li>
              <Link href="/app">Home and search</Link>
            </li>
            <li>
              <Link href="/companies/0000320193">Apple (demo)</Link>
            </li>
            <li>
              <Link href="/compare">Compare</Link>
            </li>
          </ul>
        </nav>
        <nav aria-label="Project">
          <h2 className="label-caps text-muted">Project</h2>
          <ul className="mt-3 flex flex-col gap-1.5">
            <li>
              <a href={REPO_URL} rel="noopener noreferrer">
                Source on GitHub
              </a>
            </li>
            <li>
              <a href="#faq">FAQ</a>
            </li>
            <li>
              <a href="#top">Back to top</a>
            </li>
          </ul>
        </nav>
      </div>
      <div className="border-t border-line">
        <p className="mx-auto max-w-6xl px-4 py-4 text-xs text-muted sm:px-6">© 2026 SEC Analytics (fictional)</p>
      </div>
    </footer>
  );
}
