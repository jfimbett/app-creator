import { Section } from "@/components/landing/Section";
import { HOW_IT_WORKS } from "@/lib/landing-content";

/** How it works: three numbered steps. */
export function HowItWorks() {
  return (
    <Section id="how-it-works" eyebrow="How it works" title="From a name to a cited answer in three steps" band>
      <ol className="grid gap-6 md:grid-cols-3">
        {HOW_IT_WORKS.map((step, index) => (
          <li key={step.title} className="flex gap-4">
            <span aria-hidden="true" className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent font-semibold text-on-accent">
              {index + 1}
            </span>
            <div>
              <h3 className="text-title font-semibold text-fg">
                <span className="sr-only">Step {index + 1}: </span>
                {step.title}
              </h3>
              <p className="mt-1 text-muted">{step.body}</p>
            </div>
          </li>
        ))}
      </ol>
    </Section>
  );
}
