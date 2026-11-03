# Skills and agents index

Skills live flat in `.claude/skills/<name>/SKILL.md` (no category folders, so Claude Code and Cline both find them).
This table groups them by phase. Type `/name` to use one, or let the assistant pick it when the situation
matches. Conventions: [docs/TOOLKIT.md](../../docs/TOOLKIT.md).

Guides in *italics* belong to skills maintained in other steps; open the skill's folder for the current list.

| Phase | Skill | Use it when | Key guides |
|---|---|---|---|
| Define | [product-interview](product-interview/SKILL.md) | starting a new app, product.md missing or not agreed, changing users, MVP or stack (delegated mode: a written brief answers) | *requirements-and-acceptance.md, stacks.md, templates/* |
| Define | [plan-architecture](plan-architecture/SKILL.md) | writing or changing architecture.md; before adding an endpoint, stored data, an external service, a setting, caching or a job | *api-and-contracts.md, errors-and-validation.md, caching-and-jobs.md* |
| Design | [design-interface](design-interface/SKILL.md) | creating or changing a screen, form, table, chart or navigation; the app looks confusing or cluttered | *charts-and-data-display.md, design-system.md, ui-states-and-forms.md, responsive-and-accessibility.md* |
| Build | [build-feature](build-feature/SKILL.md) | adding, changing or continuing a feature; the next slice of plan.md | — |
| Build | [integrate-api](integrate-api/SKILL.md) | getting or sending data from an external API or AI model; integrations failing, slow or rate-limited; offline fixtures | *http-client-patterns.md* |
| Build | [manage-data](manage-data/SKILL.md) | saving data between visits, caching, tables or stored files, choosing a database, background jobs, wrong or duplicated data | *caching-and-storage.md* |
| Build (optional) | [add-accounts](add-accounts/SKILL.md) | sign-up, sign-in, own-data-only, roles; only if product.md needs it | *authn-authz.md* |
| Build (optional) | [add-payments](add-payments/SKILL.md) | charging customers, subscriptions, checkout, refunds (test mode only) | — |
| Check | [test-and-check](test-and-check/SKILL.md) | writing logic, calculations, data access or permissions; deciding what to test; before saying a feature works | *playwright-journeys.md, performance.md* |
| Check | [debug-issue](debug-issue/SKILL.md) | an error, crash, wrong number, blank chart, failing test, behaviour differing from acceptance.md | *refactoring.md* |
| Check | [review-changes](review-changes/SKILL.md) | a review or audit; before merging or submitting; after a large slice or changes to accounts, payments, secrets or calculations | — |
| Ship | [prepare-deploy](prepare-deploy/SKILL.md) | running somewhere other than a laptop, sharing, handover, submission; someone cannot install from the README | *ci.md, docker.md, env-and-secrets.md, security-checklist.md* |
| Ship | [write-docs](write-docs/SKILL.md) | README, setup, troubleshooting, changelog, release notes, architecture diagram, teaching notes; docs someone could not follow | [doc-templates.md](write-docs/doc-templates.md), [checking-docs.md](write-docs/checking-docs.md) |
| Collaborate | [git-collaboration](git-collaboration/SKILL.md) | branches, commits, pull requests, review, conflicts, merge vs rebase, releases and tags, Issues, Projects, team of five, switching versions, recovery | [branching-and-prs.md](git-collaboration/branching-and-prs.md), [conflicts-merge-rebase.md](git-collaboration/conflicts-merge-rebase.md), [releases-issues-projects.md](git-collaboration/releases-issues-projects.md), [team-of-five.md](git-collaboration/team-of-five.md) |
| Coordinate | [orchestrate-steps](orchestrate-steps/SKILL.md) | splitting work into recorded steps, dispatching with `scripts/dispatch-step.mjs`, follow-ups, auditing `runs/`, gating and checkpointing | [step-records.md](orchestrate-steps/step-records.md), [manual-capture-cline.md](orchestrate-steps/manual-capture-cline.md) |

## Agents (`.claude/agents/`)

Claude Code runs these as subagents. Cline's VS Code extension does not; there, a task can follow the agent file
as instructions (see `review-changes`, "Without subagents").

| Group | Agent | One line |
|---|---|---|
| Orchestration | `project-orchestrator` | plans small recorded steps, picks skills and agents, judges results, gates milestones; read-only |
| Orchestration | `delegated-product-owner` | answers routine product-interview questions from the written brief when the owner delegated them; read-only |
| Builder | `product-architect` | turns an idea or brief into product, acceptance, architecture and API/data documents; documents only |
| Builder | `frontend-engineer` | builds screens in Next.js, React, TypeScript, Tailwind and Recharts, with states and accessibility |
| Builder | `backend-engineer` | builds FastAPI endpoints, external API clients, validation, errors, caching and storage |
| Builder | `design-lead` | design tokens, typography, layout, chart styling, responsive and accessible states |
| Builder | `test-engineer` | known-answer tests, mocked API tests, Playwright journeys, bug reproductions |
| Builder | `docs-writer` | README, setup, run and teaching docs that match tested commands; docs only |
| Coaching | `github-coach` | explains git state and proposes safe git/GitHub workflows; runs read-only git commands only |
| Reviewer | `code-reviewer` | correctness and maintainability; reports only |
| Reviewer | `test-reviewer` | missing or weak tests, edge cases, calculations, fixtures; reports only |
| Reviewer | `security-reviewer` | secrets, authorisation, sensitive data, deployment files; reports only |
| Reviewer | `ux-reviewer` | usability, accessibility and critical journeys; reports only |
