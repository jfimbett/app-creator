# PROMPT — m2-01-implement-main-session

- Sender: the instructor (owner of the repository), pasted into the top-level session on 2026-11-04
- Receiver: top-level Claude Code session (Opus 5.5), working directly; no dispatched agents
- Starting commit: 9ddd60d on main (descends from tag m1, bd8ab81; only records added after the tag)
- Workspace: isolated worktree `.worktrees/m2`, branch `work/m2`; the classroom demo keeps running from the main checkout
- Milestone brief: `milestones/02-financial-intelligence/PROMPT.md`, unchanged since `template-v1` (sha256 35112cc9b79ee530…)

<!-- DISPATCH:BEGIN -->
Proceed with M2 — Financial Intelligence ONLY. Do not begin M3.

Read GOAL.md, PROGRESS.md, the agreed product/architecture documents, and milestones/02-financial-intelligence/PROMPT.md. M1 is verified at tag m1, commit bd8ab81. Preserve that immutable checkpoint and build cumulatively from it. Preserve the later documentation records too.

Record this exact instruction before implementation. Keep the per-step prompts, follow-ups, actual final responses where accessible, test results and commit references. Explicitly mark any transcript-capture gaps.

Implement M2:
- Functioning live SEC company lookup by name, ticker or CIK.
- Annual income-statement, balance-sheet and cash-flow summaries.
- Historical charts and a selectable financial metric explorer.
- Growth, profitability, leverage and cash-flow metrics where supported by the source data.
- Clear units, fiscal periods, formulas and source provenance.
- Explicit unavailable states for unsupported facts or calculations; never replace missing data with zero or invent values.

Live data is essential: do not implement M2 using fixtures alone.
- Fetch SEC data through the FastAPI backend.
- Add a clear Live/Demo selector with retrieval or snapshot dates.
- Keep the existing offline demonstration working.
- Use an identifying SEC User-Agent, caching, conservative throttling, timeouts and appropriate error handling.
- If a genuine contact email is not already configured locally, ask me to configure it locally. Do not invent an email, print secrets or commit personal configuration.
- Verify at least one live company lookup and financial-facts retrieval. Report live failures honestly; never silently substitute fixtures.

Financial correctness:
- Distinguish annual duration facts from balance-sheet instant facts.
- Handle duplicate disclosures, restatements, concept alternatives and fiscal-year differences.
- Document the selection policy and distinguish reported from calculated values.
- Implement ratios only when their required inputs are available; handle zero denominators.
- Label these as normalized statement summaries, rather than complete reproductions of the original statements.

Work directly in the main session. Use the relevant skills and delegated product-owner decisions, but avoid nested Claude CLI processes and lengthy parallel review dispatches. Do not recreate the stalled review script. Use short commands and diagnose stalled processes promptly.

Keep the working classroom demo available on ports 3200/8200. Use separate ports or an isolated worktree for M2 verification if needed. Do not modify a checkout underneath its running demo or stop unrelated services. Once M2 passes verification, deliberately switch the classroom demo to the verified M2 version.

Run meaningful financial-data tests, lint/type checks, the production build and browser journeys covering live/demo selection, company lookup, statement summaries, metric selection and failures. Inspect the desktop interface. Preserve M1 functionality. Avoid repeating checks unless changes or failures justify it.

If M2 passes its applicable acceptance gate, create:
- branch milestone/02-financial-intelligence
- annotated tag m2

Do not weaken the acceptance criteria to claim completion. If blocked, preserve the partial work and leave the latest verified demo running.

GitHub publication, commit-email decisions, optional permission hardening and M3–M5 are deferred. Do not restore Ask permission rules or overwrite my settings changes.

Finish with:
1. The running application URL and exact restart commands.
2. What M2 adds and a three-minute demonstration script.
3. Actual test results, separating live SEC checks from fixture tests.
4. Branch/tag and commit references.
5. Remaining limitations or blockers.

Then STOP and wait for my instruction before M3.
<!-- DISPATCH:END -->
