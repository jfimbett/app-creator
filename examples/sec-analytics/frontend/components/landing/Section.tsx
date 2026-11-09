import type { ReactNode } from "react";

type SectionProps = {
  id: string;
  eyebrow: string;
  title: string;
  intro?: ReactNode;
  children: ReactNode;
  /** Raised background band, to separate neighbouring sections. */
  band?: boolean;
};

/** One landing section: anchor id, small caps eyebrow, heading (its accessible name) and content. */
export function Section({ id, eyebrow, title, intro, children, band = false }: SectionProps) {
  return (
    <section id={id} aria-labelledby={`${id}-title`} className={`scroll-mt-16 ${band ? "border-y border-line bg-panel" : ""}`}>
      <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 md:py-24">
        <p className="label-caps text-accent">{eyebrow}</p>
        <h2 id={`${id}-title`} className="mt-2 max-w-3xl text-display font-semibold tracking-tight text-fg">
          {title}
        </h2>
        {intro ? <div className="mt-3 max-w-2xl text-title text-muted">{intro}</div> : null}
        <div className="mt-10">{children}</div>
      </div>
    </section>
  );
}

/** A round avatar with initials (no photos of anyone). */
export function Initials({ initials, size = "md" }: { initials: string; size?: "md" | "lg" }) {
  const box = size === "lg" ? "h-14 w-14 text-title" : "h-10 w-10 text-base";
  return (
    <span aria-hidden="true" className={`inline-flex ${box} shrink-0 items-center justify-center rounded-full border border-line-strong bg-panel-raised font-semibold text-fg`}>
      {initials}
    </span>
  );
}
