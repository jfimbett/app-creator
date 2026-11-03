# App Creator — autonomous implementation assignment

## 1. Outcome and authority

Build a reusable, general-purpose application starter named App Creator and demonstrate it through five cumulative, working versions of SEC Analytics. This is for a business-school programming and AI course. Students primarily inspect prepared versions in class; they can also rebuild each transition with the exact implementation prompt. They later reuse the generic starter for unrelated applications and teams of about five.

Implement the work, run it, inspect the interface, and verify the deliverables. Do not stop after planning or scaffolding. Resolve ordinary product and engineering choices using this assignment. Use specialized subagents for independent implementation or review where useful; keep one owner for integration, Git history, and milestone checkpoints. Do not spawn every agent for every task.

Authorized: local development, project-local dependency installation, tests, local services, commits, and creating and pushing a NEW PUBLIC GitHub repository named app-creator under the currently authenticated personal account after verification and secret review. No further product approval is required for those actions. Do not deploy to cloud hosting. Do not modify unrelated repositories, global settings, existing remote repositories, credentials, or organization settings. Never force-push or overwrite an existing remote repository. If publication is blocked, finish and verify the local deliverables and report the precise blocker.

Unattended execution is best effort: tool policies, authentication, quota, network access and execution limits still apply. Do not claim this prompt bypasses them. Save resumable progress throughout.

## 2. Audit before changing anything

Inspect the actual folder, instructions, Git status, remotes, existing starter, installed skills/plugins, tools, and runtime versions. Do not assume the starter ZIP described in an earlier chat is present. If present, preserve its real capabilities and useful files; if absent, create the toolkit specified below and explicitly record that it was reconstructed, not inspected or preserved from a ZIP.

Preserve unrelated user changes. Do not run destructive cleanup, blindly overwrite files, or initialize Git inside another repository. If an existing checkout needs isolation, use a new sibling workspace or branch and record its path. Read applicable project instructions. Resolve a routine interview requirement with the already-complete product brief here; do not silently disable security policies or user instructions.

Check git, GitHub CLI authentication, commit identity, Node/npm, Python, package installation, and browser availability early. Use supported compatible dependency versions verified against official documentation. Pin exact resolved dependencies in lockfiles. Do not invent an author identity or install system packages without authorization. Record blockers while continuing independent tasks.

Create PROGRESS.md immediately: decisions, actual paths, current phase, next actions, commands, failures, checkpoint SHAs and publication status. Keep commands and logs free of secrets. Use this file to resume after interruptions; it does not itself restart a terminated session.

## 3. Structure and generic starter

Use this structure, adapting only when the actual starter makes an equivalent structure preferable:

```text
.claude/skills/<skill-name>/SKILL.md
.claude/agents/<agent-name>.md
CLAUDE.md
AGENTS.md
START-HERE.md
AI-USAGE.md
PROMPTS.md
GOAL.md
PROGRESS.md
examples/sec-analytics/frontend/
examples/sec-analytics/backend/
examples/sec-analytics/fixtures/
examples/sec-analytics/CLAUDE.md
milestones/01-foundation/PROMPT.md
milestones/02-financial-intelligence/PROMPT.md
milestones/03-filing-intelligence/PROMPT.md
milestones/04-comparative-analysis/PROMPT.md
milestones/05-ai-financial-analyst/PROMPT.md
docs/
scripts/
```

Keep global project instructions short and generic. Put finance-specific rules and references with the SEC example. Organize skills through an index, not extra category directories that break discovery. Confirm current Claude Code skill/subagent formats from official documentation. Every skill needs valid frontmatter, useful trigger descriptions, concrete workflows, examples, checks, failure handling and relevant supporting references. Avoid dozens of repetitive, generic files; cover the requested capabilities through coherent skills with supporting guides.

Preserve or reconstruct and improve these starter capabilities: product-interview, design-interface, test-and-check, debug-issue, add-accounts, build-feature, integrate-api, review-changes, add-payments, prepare-deploy, manage-data; plus code-reviewer, security-reviewer, ux-reviewer and test-reviewer. Preserve useful Cline rules and ignore files if present. Explain how Cline users read equivalent task instructions; do not claim Cline executes Claude-specific subagents or slash commands identically. Test Cline only if it is actually available and configured; otherwise label compatibility untested.

Expand coverage to requirements/MVP/acceptance criteria, architecture, API/database design, authentication/authorization, validation, error handling, caching/jobs, design systems, typography, responsive/accessibility, charts, forms, UI states, debugging/refactoring, meaningful tests, performance, security, documentation, environment/secrets, CI, Docker and deployment preparation. These are reusable instructions, not a requirement to implement accounts, payments, jobs, databases or Docker in the SEC example.

Give Git/GitHub substantial practical coverage: branches, small commits, PRs/review, conflict resolution, merge versus rebase, releases, Issues, Projects, branch protection and five-person collaboration. Distinguish local actions from publication. Include safe command examples and avoid destructive reset/clean or shared-history rewriting as default advice.

Add focused agents for orchestration, product/architecture, frontend, backend, design, GitHub coaching, testing and documentation where they add value. Introduce SEC-specific expertise when implementing the example rather than putting financial assumptions into the generic starter. Validate actual skill discovery after creation; if the running session needs restarting to load agents, report it and continue implementation with explicit instructions rather than stopping.

Create a clean `template` branch and immutable `template-v1` tag at the generic-toolkit checkpoint BEFORE adding the SEC application. It must include a simple generic getting-started path and all five example build prompts, but no implemented SEC application. Explain that `main` will contain the complete example, while students use `template` when starting a different app. The generic starter must not require downloading the SEC example to work.

## 4. Runtime and classroom reliability

Use Next.js/React/TypeScript, Tailwind, shadcn/ui where appropriate, Recharts, and a Python FastAPI backend. Use a simple local disk cache or SQLite only when needed; no PostgreSQL, accounts, payments, vector database, hosted service or Docker prerequisite. No Streamlit. Keep client-to-server integration consistent, preferably same-origin requests via a development proxy.

Expose and document these stable commands from the repository root, working at EVERY milestone and portable to macOS and Windows:

```bash
npm run setup
npm run dev
npm run verify
npm run demo
```

`setup` installs locked frontend dependencies, creates an isolated Python virtual environment, installs locked backend dependencies and installs the required project-local browser binary. It must be idempotent and detect supported Python/Node versions. Do not use global pip/npm packages. The root launcher must avoid recursively invoking its own setup command. `dev` starts both services and cleans up its own processes. `demo` starts both in explicit fixture mode without API keys or SEC network access. `verify` runs the milestone's relevant checks and exits nonzero on failure. Document the initial root `npm ci` needed to install launcher dependencies. Provide .env.example and troubleshooting for occupied ports, proxies, Windows and switching versions. Never kill unrelated services.

Build a deterministic offline classroom demonstration using compact authentic SEC snapshots for at least three nonfinancial US-GAAP companies, preferably AAPL, MSFT and GOOGL, with several annual periods and filing excerpts. Record source URL, retrieval date, accession, reporting periods and fixture scope. If network access prevents obtaining authentic fixtures, report that limitation; never manufacture values or label synthetic data as SEC data. Synthetic fixtures may support tests if clearly isolated and marked.

The interface must visibly distinguish live data, cached data, recorded SEC demo data and missing data. Show snapshot/as-of dates. An old snapshot must never appear as the current latest filing. Do not silently substitute fixture companies when a live search fails. Provide an explicit demo-mode choice. Do not download SEC bulk archives for this small example.

## 5. Product and five milestones

Use a modern Bloomberg-inspired dark navy terminal: dense readable tables, tabular numerals, clear hierarchy, restrained accents, consistent spacing, keyboard-friendly search, useful charts, compact navigation and responsive layouts. Avoid decorative card grids and nonfunctional controls. Dark mode is required; light mode is secondary after core functionality. Include realistic loading, empty, missing-data, offline and error states. Do not invent company descriptions or market prices.

| Milestone | Required behavior |
| --- | --- |
| 01 Foundation | Polished shell; company search by name, ticker or normalized CIK over the demo universe; profile and identifiers; basic interactive dashboard using explicitly labelled fixtures; stable launch scripts and meaningful browser smoke test. |
| 02 Financial intelligence | Backend SEC adapters; live company lookup; annual income statement, balance sheet and cash-flow summaries; 5–10 available years; selectable metric explorer and charts; source provenance and calculated ratios; explicit missing-data behavior. |
| 03 Filing intelligence | Latest available 10-K and 10-Q metadata and actual filing text; history with amendment labels; readable filing view, section navigation and text search; source links; documented fallback when section extraction is imperfect. |
| 04 Comparative analysis | Compare 2–4 companies; selectable revenue/growth/margin/leverage/cash-flow metrics; comparable tables/charts with fiscal dates and units; clearly labelled indexing or normalization; CSV export. |
| 05 AI analyst | Optional OpenRouter settings and company/filing/comparison chat grounded in application data, with validated source references, bounded context/output, connection testing and graceful failures. All non-AI functions continue without a key. |

Each version must preserve previous behavior and work as an independent checkout. At M1 explain the limited fixture search universe; later live search must not be presented as supporting arbitrary non-SEC companies. Do not add unfinished future navigation that looks functional.

## 6. SEC correctness

Read current official SEC API and fair-access documentation. SEC calls belong in the backend, not browser requests to data.sec.gov. Live requests require a descriptive identifying User-Agent with a genuine contact email configured locally; never invent one. Offline demo mode must work without that setting. A setup input or local environment file may collect it without committing it.

Use submissions, Company Facts, ticker lookup and actual EDGAR archive documents. Normalize CIK input; construct and validate archive URLs. Handle older submissions metadata when needed. Restrict fetches to approved SEC hosts and paths, including redirects; do not implement an arbitrary URL proxy. Cache, deduplicate, use timeouts and backoff, honor retry headers and throttle conservatively below SEC limits. A classroom sharing one public IP needs aggregate consideration: default to fixtures/caches, not a burst of uncached requests from every student. Do not bypass 403 restrictions or disguise automated traffic.

Company Facts is not a ready-made financial statement. Document concept mappings and render explicitly labelled normalized statement summaries, not a supposedly exact complete reproduction. Track concept, taxonomy, unit, start/end, fiscal dates, form, accession, filing date, source URL and whether each number is reported or derived. Preserve the source facts used.

Distinguish duration and instant facts. Never group observations by `fy` alone, mix annual and quarterly/YTD durations, or sum duplicated disclosures. Annual durations must accommodate 52/53-week calendars. Apply and document a deterministic restatement/duplicate policy. Do not imply point-in-time historical data if using later restatements. Test alternate revenue concepts, missing tags, duplicate filings, negative/zero values and incompatible units.

Required metrics when inputs support them: revenue/growth; operating income; net income/margins; operating cash flow, capex and FCF; assets, liabilities/equity; debt-to-equity and working capital; ROE and ROA using average beginning/end equity/assets when available. Display unavailable ratios when a required input is missing or a denominator is zero; document interpretation for negative equity. Never silently substitute operating income for EBIT. Define derived EBIT/EBITDA precisely and show unavailable if needed inputs cannot be supported. Avoid market valuation metrics without a market-price source. Preserve reporting currencies and fiscal year ends in comparisons; no silent currency conversion or calendar alignment. Missing values are null, never zero. Include formula/provenance tooltips.

Treat retrieved filing HTML and text as untrusted content. Prefer sanitized text rendering, strip scripts/active content, avoid unsafe raw HTML, and preserve source links. Section extraction must handle repeated TOC headings and explain uncertainty; do not claim guaranteed semantic extraction.

## 7. OpenRouter analyst

Provide masked key input, model selection/manual model ID, test connection, status, clear-key action and a visible indication when AI is unavailable. Default to memory-only key storage; optional session persistence requires explicit opt-in and a clear explanation that browser storage is accessible to scripts. Do not implement persistent localStorage key storage by default or describe it as encrypted/secure. Never commit keys, place them in public frontend environment variables, include them in logs/errors/screenshots or save them in server files.

Forward the user-supplied key to the local backend for the specific OpenRouter request, held only transiently. Redact request bodies and authorization headers; use localhost binding, narrow CORS/origin handling, request limits and upstream timeouts. This is a local teaching app, not a ready-to-expose public inference proxy.

Verify current OpenRouter endpoints and model availability from official docs. Model choice is configurable; do not hardcode an assumed cheap/free model from memory. Display model IDs and available pricing when obtainable; handle retired models and 401/402/429/timeouts. Only run paid live AI validation if a test key is already available locally for that purpose. Do not ask for a secret in chat, spend on repeated automatic retries, or invent a successful live test. Mocked integration and live verification must be reported separately.

Use bounded deterministic retrieval of financial facts and relevant filing passages; no vector database is required. Compute numerical results in application code. Assign source IDs server-side and validate returned references against the supplied sources. Explain the difference between source-link validity and claim correctness. Do not promise hallucinations are impossible. Treat filings as data, never instructions. Test prompt-injection handling, unsupported questions, missing context and invalid citations. Cite filing passages and fact sources with date/period. Cap request size, output tokens and concurrency; provide cancel/error handling. A connection test may incur a small charge and should say so.

Document issuing separate limited-credit keys per student or group instead of distributing an unrestricted shared key. Keep app AI configuration distinct from the model/provider configuration of Claude Code or Cline.

## 8. Prompts, chronology and Git checkpoints

This order is mandatory: commit the toolkit and all five self-contained build prompts FIRST; then implement M1, verify and checkpoint it; then M2, verify and checkpoint it; and so on. Do not build M5 first and attempt to manufacture earlier history afterward.

Write all five PROMPT.md files before the template checkpoint. Each must specify the exact starting ref, context, new work, design, architecture, no-interview defaults, tests and acceptance criteria. M1 starts from `template-v1`; M2 starts from `m1`; M3 from `m2`; M4 from `m3`; M5 from `m4`. A completed M2 checkout is for inspecting M2, not building it with the M2 prompt.

Actually use the recorded prompt to initiate each implementation, via a focused subagent or equivalent explicit task handoff. The owner integrates and tests. Before any implementation-changing follow-up, save its exact text in the milestone's FOLLOWUPS.md. Log tool-driven repairs and deviations. Do not retroactively pretend a cleaner final prompt was the exact prompt used. Replaying a prompt does not guarantee identical generated code; Git checkpoints are the authoritative prepared versions.

Record for each milestone: starting ref/SHA, prompt path/hash, follow-ups, result SHA in a final manifest, features, changes, checks, screenshots inspected and limitations. Avoid circular self-SHA files: keep the complete result-SHA manifest in final documentation after the checkpoint commits.

At each successful checkpoint immediately create its branch and annotated tag:

| Branch | Tag |
| --- | --- |
| template | template-v1 |
| milestone/01-foundation | m1 |
| milestone/02-financial-intelligence | m2 |
| milestone/03-filing-intelligence | m3 |
| milestone/04-comparative-analysis | m4 |
| milestone/05-ai-financial-analyst | m5 |

Advance one cumulative build history and finally main. Never point all milestone branches at M5. Verify ancestry and inspect diffs for later-feature leakage. Final main may contain final reports after M5; document its relationship to m5. Do not move an existing tag silently. If historical verification finds a defect, correct it through an explicit documented repair preserving cumulative ancestry; do not merely fix main and declare old refs healthy.

Verify every final ref in an isolated clean worktree, with its own installed dependencies, ports, caches and environment. Avoid checking branches in a directory used by running services. Remove only temporary worktrees/services created by this task, preserving logs and reports. Do not require ignored .env files or untracked implementation files from the original working directory for success.

### Mandatory supervisor, product-owner role and step records

Five milestones are five student-facing releases, NOT five iterations or five agent calls. Break each milestone into as many meaningful feature, integration, review and repair steps as required. Do not impose an arbitrary step count. Keep useful intermediate commits as well as the five verified checkpoints.

Create and actually use a `project-orchestrator` agent and a separate `delegated-product-owner` agent. The top-level Claude session owns integration and invokes these agents; do not assume a subagent can spawn further agents unless the installed version supports that capability. The orchestrator plans small steps, selects the relevant skills and specialists, checks outputs against acceptance criteria, requests repairs, and gates milestones on actual verification. Record who performed each role rather than claiming nonexistent delegation.

The delegated product owner answers the `product-interview` skill's routine product questions on the instructor's behalf using GOAL.md and the already recorded decisions. It must not restart an interview with the instructor. Save the questions, exact answers and their basis in docs/PRODUCT-DECISIONS.md; distinguish explicit instructor requirements from delegated assumptions. For unspecified reversible details, choose a sensible default and record it. This delegation does not authorize new expenditure, scope changes, different publication destinations or disclosure of secrets. If genuinely blocked, document the blocker and continue independent authorized work. Populate the agreed product/architecture/acceptance/plan documents from these decisions before implementation.

At every meaningful step, including planning, delegated interviews, feature builds, reviews and repairs, keep an append-only record under `runs/<milestone-or-bootstrap>/<step-id>/`:

- `PROMPT.md`: the exact dispatched task text, saved BEFORE dispatch; identify the sending and receiving roles, starting commit, loaded skill names and instruction/reference paths. Preserve any referenced instruction revision or content hash. Include exact skill arguments and follow-up prompts. Do not replace the actual prompt with a reconstructed summary.
- `RESPONSE.md`: the verbatim final returned assistant/subagent message for that step, saved immediately after receipt. Require each task to return a concise handoff containing changes, verification evidence, remaining findings and next action. Keep orchestrator summaries separately; never present a summary as the original response.
- `RESULT.json`: timestamps, role, milestone, task status, starting/result commits where available, checks and exit codes, evidence paths, follow-up relationships and any missing record. Avoid recording a commit's own SHA inside that same commit; add the result SHA in the subsequent log update or final manifest.

Maintain `runs/INDEX.md` with ordered links to every step and separate milestone boundaries. Include failed attempts and review-driven corrections. Record shell commands/results needed to understand verification in bounded step logs; this is a record of observable instructions, messages, actions and results, not private reasoning. Redact credentials and personal data using explicit redaction markers; never retain secrets merely for transcript fidelity. Do not log a final message that has not yet been emitted. The final build response should identify any uncaptured top-level message and provide the session/export reference when actually available; never invent transcript access.

Use actual returned subagent messages or available supported session exports to capture responses. Verify any export mechanism against the installed CLI rather than assuming undocumented paths. If capture fails, mark the gap explicitly and repair the logging workflow before dispatching further steps. The owner must audit that every dispatched step has its prompt and final returned message, or a clear failure/missing-message marker. No fabricated retrospective conversations.

Keep each milestone's top-level PROMPT.md as the exact transition brief and link it to the detailed ordered step records and FOLLOWUPS.md. A polished optional classroom replay prompt must be labelled as edited teaching material, distinct from the execution record. Provide the final transcript index and explain that exact prompts and outputs document the process but cannot guarantee deterministic regeneration.

## 9. Verification and teaching deliverables

Use pytest for backend/data logic; appropriate frontend checks; project-local Playwright for browser journeys. At each checkpoint run lint/type checks, relevant tests, production frontend build, both services and a browser smoke flow. Visually inspect desktop and narrow layouts. Include numerical mapping tests, proxy failures, missing data, fiscal comparability, filing sanitization, CSV correctness and AI key/citation handling as introduced. Prefer a few meaningful checks over large tests that mirror code.

Run fixture verification independently of SEC/OpenRouter network availability. Separately attempt live SEC smoke checks when correctly identified and live OpenRouter checks only with authorized test credentials. Record blocked, failed, skipped and passed accurately. M5 without a paid test key can have verified mocked integration with live AI explicitly unverified. Do not call that live verification complete. Do not let an unreachable external service prevent completing offline functionality.

Create:

- README.md and START-HERE.md: two paths, inspect prepared SEC milestones versus start a new generic app.
- docs/SETUP.md: actual tested commands, supported versions, offline/live modes, contact User-Agent and OpenRouter setup, switching versions, troubleshooting.
- docs/ARCHITECTURE.md and a compact diagram of frontend/backend/SEC/OpenRouter boundaries.
- docs/TEACHING-GUIDE.md: a quick instructor rehearsal, exact checkout commands, three-minute demonstration per milestone, relevant skills/agents, prompt reconstruction, student exercises and known limitations.
- docs/GITHUB-COLLABORATION.md: five-person roles, shared contracts, feature branches, PRs/reviews/conflicts, suggested protections, fork/origin/upstream distinctions, no policy changes applied automatically.
- docs/CHANGELOG.md and each milestone README: actual additions and limitations.
- docs/FINAL-VERIFICATION.md: final refs/SHAs, environment, exact checks/results, visual findings and live-versus-fixture/mock evidence.
- docs/PROMPT-EXECUTION-LOG.md: exact prompt/follow-up provenance and any deviations.
- docs/SOURCES.md: official technical sources and fixture provenance.

Show students both workflows with the actual repository URL after publication:

```bash
# Inspect a prepared version (from main after a normal clone)
git fetch origin --tags
git switch --detach m1
npm ci
npm run setup
npm run demo
```

```bash
# Rebuild M2 from its actual starting point in a separate clean checkout
git switch -c exercise/build-m2 m1
claude
# Read milestones/02-financial-intelligence/PROMPT.md and implement it.
```

Explain stopping services before switching refs, checking git status, preserving student edits and rerunning setup because dependencies may change. Never advise a destructive reset to make checkout work.

## 10. Publication and completion

Check the authenticated personal owner and whether OWNER/app-creator exists. An existence query failing due to authentication/network access is not proof the name is available. If it exists or origin is already configured, do not overwrite or push into it without explicit existing authorization; report the conflict and finish locally. Create only the agreed new repository, public, using authenticated gh CLI.

Before any push inspect staged/tracked files and history for keys, tokens, .env, private correspondence and unintended files. Use available secret scanning plus review; no scan is a guarantee. Exclude dependencies, caches, generated local logs, credentials and personal contact configuration. Include a documented suitable code license while preserving existing notices.

Push main and only the named template/milestone branches and tags with explicit refspecs, not every unrelated local branch/tag. Set main as default. Verify remote refs match local SHAs. Run CI against the prepared versions or a reproducible milestone matrix using fixtures. If CI cannot run, distinguish locally verified from CI verified. Publish no hosting deployment and incur no cloud service costs.

The final response must provide the actual path/URL, refs/SHAs, five milestone summaries, toolkit inventory, exact instructor/student launch commands, test evidence, publication status and remaining limitations. If something is incomplete, state exactly what and how to resume. Do not equate created files with verified functionality, claim the overnight deadline is guaranteed, or omit failures to present a finished result.

Start now: audit, checkpoint the plan, create the reusable toolkit and immutable prompts, then implement and verify each milestone in sequence through publication.
