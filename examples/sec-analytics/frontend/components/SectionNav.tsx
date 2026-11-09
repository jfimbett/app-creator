"use client";

import { useEffect, useState } from "react";

import type { FilingSection } from "@/lib/types";

type Props = {
  status: "detected" | "not_detected";
  note: string;
  sections: readonly FilingSection[];
  onJump: (blockId: number) => void;
};

function sectionLabel(section: FilingSection): string {
  return section.title ? `${section.item} · ${section.title}` : section.item;
}

/** Which section the reader is in: the last heading above the middle of the upper screen. */
function useActiveSection(sections: readonly FilingSection[]): string | null {
  const [active, setActive] = useState<string | null>(null);
  useEffect(() => {
    if (sections.length === 0) return;
    let frame = 0;
    const measure = () => {
      frame = 0;
      let found: string | null = null;
      for (const section of sections) {
        const element = document.getElementById(`block-${section.block_start}`);
        if (element && element.getBoundingClientRect().top <= window.innerHeight / 3) found = section.id;
      }
      setActive(found);
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(measure);
    };
    measure();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      if (frame) cancelAnimationFrame(frame);
    };
  }, [sections]);
  return active;
}

/** Sections as a rail on desktop and a select on a phone, or the labelled note when none were found. */
export function SectionNav({ status, note, sections, onJump }: Props) {
  const active = useActiveSection(sections);

  if (status === "not_detected") {
    return (
      <aside aria-label="Sections" className="lg:sticky lg:top-[4.5rem] lg:self-start">
        <p data-testid="section-note" data-status={status} className="rounded-md border border-l-[3px] border-line border-l-warning bg-panel-raised px-3 py-2 text-table text-warning">
          {note}
        </p>
      </aside>
    );
  }

  return (
    <aside aria-label="Sections" className="flex min-w-0 flex-col gap-2 lg:sticky lg:top-[4.5rem] lg:max-h-[calc(100vh-5.5rem)] lg:self-start">
      <p data-testid="section-note" data-status={status} className="text-table text-muted">
        {note}
      </p>
      <label className="flex flex-col gap-1 text-table lg:hidden">
        <span className="label-caps text-muted">Sections</span>
        <select
          data-testid="section-select"
          value={active ?? ""}
          onChange={(event) => {
            const target = sections.find((section) => section.id === event.target.value);
            if (target) onJump(target.block_start);
          }}
          className="field w-full py-1.5"
        >
          <option value="" disabled>
            Jump to a section
          </option>
          {sections.map((section) => (
            <option key={section.id} value={section.id}>
              {sectionLabel(section)}
            </option>
          ))}
        </select>
      </label>
      <nav data-testid="section-rail" aria-label="Filing sections" className="surface hidden min-h-0 overflow-y-auto py-1 lg:block">
        <ul>
          {sections.map((section) => (
            <li key={section.id}>
              <button
                type="button"
                data-section={section.id}
                aria-current={active === section.id ? "true" : undefined}
                onClick={() => onJump(section.block_start)}
                className={`block w-full border-l-2 px-3 py-1.5 text-left text-table transition-colors duration-[var(--dur-fast)] hover:bg-panel-raised ${active === section.id ? "border-accent bg-panel-raised text-fg" : "border-transparent text-muted"}`}
              >
                <span className="font-semibold text-fg">{section.item}</span>
                {section.title ? <span className="block [overflow-wrap:anywhere]">{section.title}</span> : null}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
