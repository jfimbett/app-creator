import { Initials, Section } from "@/components/landing/Section";
import { ABOUT, ABOUT_LABEL } from "@/lib/landing-content";

/** About (#about): a fictional company story and team (O5), labelled as fictional. */
export function About() {
  return (
    <Section
      id="about"
      eyebrow="About"
      title="A small team that likes numbers with sources"
      intro={
        <p data-testid="about-label" className="inline-flex items-center gap-2 rounded-md border border-warning px-2.5 py-1 text-base font-semibold text-warning">
          {ABOUT_LABEL}
        </p>
      }
    >
      <div className="grid gap-10 lg:grid-cols-[3fr_2fr]">
        <div className="flex flex-col gap-4 text-title text-fg">
          {ABOUT.story.map((paragraph) => (
            <p key={paragraph.slice(0, 24)}>{paragraph}</p>
          ))}
          <ul className="mt-2 grid gap-3 sm:grid-cols-3">
            {ABOUT.values.map((value) => (
              <li key={value.title} className="rounded-lg border border-line bg-panel p-4">
                <h3 className="text-base font-semibold text-fg">{value.title}</h3>
                <p className="mt-1 text-base text-muted">{value.body}</p>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="label-caps text-muted">The team</h3>
          <ul className="mt-3 flex flex-col gap-3">
            {ABOUT.team.map((person) => (
              <li key={person.name} className="flex items-center gap-3">
                <Initials initials={person.initials} />
                <div>
                  <p className="font-semibold text-fg">{person.name}</p>
                  <p className="text-xs text-muted">{person.role}</p>
                </div>
              </li>
            ))}
          </ul>
          <dl className="mt-6 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1">
            <dt className="text-muted">Based in</dt>
            <dd className="text-fg">{ABOUT.city}</dd>
            <dt className="text-muted">Contact</dt>
            <dd>
              <a href={`mailto:${ABOUT.contact}`}>{ABOUT.contact}</a>
            </dd>
          </dl>
        </div>
      </div>
    </Section>
  );
}
