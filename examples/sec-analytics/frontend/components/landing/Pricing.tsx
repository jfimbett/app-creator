import Link from "next/link";

import { Section } from "@/components/landing/Section";
import { PRICING_NOTE, PRICING_TIERS } from "@/lib/landing-content";

/**
 * Pricing (#pricing): three illustrative tiers (O4). There is no checkout, sign-up or plan state: every button
 * goes to the app or to a section of this page, and the note under the cards says no payments are taken.
 */
export function Pricing() {
  return (
    <Section id="pricing" eyebrow="Pricing" title="Simple, illustrative pricing" intro="The whole app is free to use in this course. The paid tiers show what a real product might offer." band>
      <ul className="grid items-stretch gap-4 lg:grid-cols-3">
        {PRICING_TIERS.map((tier) => (
          <li
            key={tier.name}
            className={`relative flex flex-col rounded-lg border bg-bg p-6 ${tier.highlighted ? "border-accent shadow-pop ring-1 ring-accent" : "border-line shadow-card"}`}
          >
            {tier.highlighted ? <p className="label-caps absolute -top-3 left-6 rounded-full bg-accent px-2.5 py-0.5 text-on-accent">Illustrative</p> : null}
            <h3 className="text-title font-semibold text-fg">{tier.name}</h3>
            <p className="mt-1 text-muted">{tier.summary}</p>
            <p className="mt-5 flex items-baseline gap-2">
              <span className="num text-display font-semibold text-fg">{tier.price}</span>
              <span className="text-muted">{tier.period}</span>
            </p>
            <ul className="mt-5 flex flex-1 flex-col gap-2">
              {tier.features.map((feature) => (
                <li key={feature} className="flex gap-2 text-fg">
                  <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--positive)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="mt-0.5 shrink-0">
                    <path d="M5 12l5 5L20 7" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
            <Link
              href={tier.cta.href}
              className={`mt-6 rounded-md px-4 py-2 text-center font-semibold no-underline hover:no-underline ${
                tier.highlighted ? "bg-accent text-on-accent hover:opacity-90" : "border border-line-strong text-fg hover:bg-panel-raised"
              }`}
            >
              {tier.cta.label}
            </Link>
          </li>
        ))}
      </ul>
      <p data-testid="pricing-note" className="mt-6 text-center text-base font-semibold text-warning">
        {PRICING_NOTE}
      </p>
    </Section>
  );
}
