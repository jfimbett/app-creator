import { Initials, Section } from "@/components/landing/Section";
import { REVIEWS_LABEL, TESTIMONIALS } from "@/lib/landing-content";

function Stars({ count }: { count: number }) {
  return (
    <p className="flex items-center gap-0.5 text-accent">
      <span className="sr-only">{count} out of 5 stars (fictional)</span>
      {Array.from({ length: 5 }, (_, index) => (
        <svg key={index} aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill={index < count ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5">
          <path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z" />
        </svg>
      ))}
    </p>
  );
}

/** Reviews (#reviews): fictional testimonials, labelled as fictional right under the heading (O3). */
export function Testimonials() {
  return (
    <Section
      id="reviews"
      eyebrow="Reviews"
      title="What students and teachers say"
      intro={
        <p data-testid="reviews-label" className="inline-flex items-center gap-2 rounded-md border border-warning px-2.5 py-1 text-base font-semibold text-warning">
          {REVIEWS_LABEL}
        </p>
      }
    >
      <ul className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {TESTIMONIALS.map((t) => (
          <li key={t.name} className="flex flex-col rounded-lg border border-line bg-panel p-5 shadow-card">
            {t.stars ? <Stars count={t.stars} /> : null}
            <blockquote className="mt-3 flex-1 text-fg">“{t.quote}”</blockquote>
            <div className="mt-5 flex items-center gap-3">
              <Initials initials={t.initials} />
              <div className="min-w-0">
                <p className="font-semibold text-fg">{t.name}</p>
                <p className="text-xs text-muted">
                  {t.role}
                  {t.organisation ? `, ${t.organisation}` : ""}
                </p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </Section>
  );
}
