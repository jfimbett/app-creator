import { Section } from "@/components/landing/Section";
import { ThemedShot } from "@/components/landing/ThemedShot";
import { FEATURES, type FeatureIcon } from "@/lib/landing-content";

const ICON_PATHS: Record<FeatureIcon, string> = {
  search: "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zm9 16-4.35-4.35",
  table: "M4 5h16v14H4zM4 10h16M10 10v9",
  document: "M7 3h7l5 5v13H7zM14 3v5h5M10 13h6M10 17h6",
  compare: "M5 20V10M10 20V4M15 20v-7M20 20V8",
  spark: "M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9zM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z",
  offline: "M3 12a9 9 0 0 1 15.36-6.36M21 12a9 9 0 0 1-15.36 6.36M12 8v4l3 2",
};

/** Features (#features): six things the app really does at m5, then two real screenshots. */
export function Features() {
  return (
    <Section id="features" eyebrow="Features" title="Everything comes with its source" intro="Built for students who need to explain where every number came from.">
      <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((feature) => (
          <li key={feature.title} className="rounded-lg border border-line bg-panel p-5 shadow-card">
            <span aria-hidden="true" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-line bg-panel-raised text-accent">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d={ICON_PATHS[feature.icon]} />
              </svg>
            </span>
            <h3 className="mt-4 text-title font-semibold text-fg">{feature.title}</h3>
            <p className="mt-2 text-muted">{feature.body}</p>
          </li>
        ))}
      </ul>

      <div className="mt-12 grid gap-6 lg:grid-cols-2">
        <figure className="min-w-0">
          <div className="overflow-hidden rounded-lg border border-line shadow-card">
            <ThemedShot
              stem="feature-compare"
              width={1200}
              height={760}
              sizes="(min-width: 1024px) 560px, 100vw"
              alt="The Compare screen with Apple, Microsoft and Alphabet: revenue by each company's own fiscal year, with the note that fiscal years are not aligned."
            />
          </div>
          <figcaption className="mt-2 text-xs text-muted">Compare: each company on its own fiscal years, never silently aligned.</figcaption>
        </figure>
        <figure className="min-w-0">
          <div className="overflow-hidden rounded-lg border border-line shadow-card">
            <ThemedShot
              stem="feature-reader"
              width={1200}
              height={760}
              sizes="(min-width: 1024px) 560px, 100vw"
              alt="The filing reader showing Apple's 10-K as clean text with a list of sections and a search box."
            />
          </div>
          <figcaption className="mt-2 text-xs text-muted">The filings reader: the 10-K as text, with sections and search.</figcaption>
        </figure>
      </div>
    </Section>
  );
}
