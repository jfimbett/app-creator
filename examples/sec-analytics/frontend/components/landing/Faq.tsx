import { Section } from "@/components/landing/Section";
import { FAQ } from "@/lib/landing-content";

/** FAQ (#faq): native <details> items, so they open with the keyboard and without JavaScript. */
export function Faq() {
  return (
    <Section id="faq" eyebrow="FAQ" title="Questions people ask" band>
      <div className="mx-auto flex max-w-3xl flex-col gap-3">
        {FAQ.map((item) => (
          <details key={item.question} className="group rounded-lg border border-line bg-bg px-5 py-4 open:shadow-card">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-title font-semibold text-fg [&::-webkit-details-marker]:hidden">
              {item.question}
              <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="shrink-0 text-muted transition-transform duration-[var(--dur)] group-open:rotate-180">
                <path d="M6 9l6 6 6-6" />
              </svg>
            </summary>
            <p className="mt-3 text-muted">{item.answer}</p>
          </details>
        ))}
      </div>
    </Section>
  );
}
