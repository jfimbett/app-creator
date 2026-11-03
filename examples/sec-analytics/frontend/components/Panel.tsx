import type { ReactNode } from "react";

type PanelProps = {
  /** Small uppercase title; also the panel's accessible name. */
  title: string;
  /** Usually a SourceBadge, shown at the right of the title row. */
  badge?: ReactNode;
  children: ReactNode;
  className?: string;
  id?: string;
};

/** Bordered panel with a title row and its source badge at the right (brief §4 layout). */
export function Panel({ title, badge, children, className, id }: PanelProps) {
  const headingId = `${id ?? title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-title`;
  return (
    <section aria-labelledby={headingId} id={id} className={`min-w-0 border border-line bg-panel ${className ?? ""}`}>
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-3 py-1.5">
        <h2 id={headingId} className="label-caps text-muted">
          {title}
        </h2>
        {badge}
      </div>
      <div className="p-3">{children}</div>
    </section>
  );
}
