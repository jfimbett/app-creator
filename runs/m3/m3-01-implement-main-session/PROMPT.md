# PROMPT — m3-01-implement-main-session

- Sender: the instructor (owner of the repository), pasted into the top-level session on 2026-11-04
- Receiver: top-level Claude Code session (Opus 5.5), working directly; no dispatched agents
- Starting commit: 6088a29 on main (descends from tag m2, 4451d43; only records added after the tag)
- Workspace: isolated worktree `.worktrees/m3`, branch `work/m3`; the classroom M2 app keeps running from the main checkout
- Milestone brief: `milestones/03-filing-intelligence/PROMPT.md`, unchanged since `template-v1`

<!-- DISPATCH:BEGIN -->
Proceed with M3 — Filing Intelligence ONLY. M4 and M5 are deferred until after class.

Read the recorded M3 prompt, GOAL.md, PROGRESS.md and the current architecture. M2 passed at tag m2, commit 4451d43; main also contains later execution records. Preserve those records and keep m1/m2 tags unchanged.

Save this exact instruction before implementation. Record implementation prompts, follow-ups, actual responses where accessible, checks and commits. Mark capture gaps honestly.

Deliver:
1. Company filing history for 10-K and 10-Q reports, showing form, filing date, reporting period and amendment labels.
2. Open the latest available annual or quarterly report, clearly distinguishing original filings from amendments.
3. Read the actual filing text inside the app.
4. Search within the filing text.
5. Navigate detected sections, with an explicit fallback if reliable section extraction is unavailable.
6. Open the original document on SEC.gov.

Use the existing SEC backend client, identifying User-Agent, cache, throttling and error handling. Fetch the primary filing document from validated SEC archive URLs. Never create an arbitrary URL proxy. Treat filing content as untrusted: render sanitized text without executing embedded HTML or scripts.

Make Live mode retrieve actual filings. Preserve offline classroom mode with a compact, authentic recorded filing or excerpt, clearly labelled with its source, snapshot date and scope. Never present an excerpt as the full document or a recorded filing as the latest live report.

Prioritize a reliable filing list and readable, searchable document before sophisticated section extraction. Do not add AI summaries or comparison features.

Work directly in this session. Avoid nested Claude CLI processes, parallel review dispatch scripts and unrelated toolkit work. Use short commands and diagnose stalled operations promptly.

Keep the verified M2 classroom application running at port 3200 with backend 8200 while implementing M3 in an isolated worktree with separate ports. Do not change files underneath the running M2 application. After M3 passes, deliberately switch the classroom application to M3. If M3 is blocked, leave M2 available.

Verify:
- Existing M2 functionality remains working.
- Filing history, document retrieval, dates, amendments and source links.
- Text search and section navigation/fallback.
- Sanitization, invalid paths and unavailable documents.
- One live SEC filing retrieval.
- One complete browser journey and desktop visual inspection.
- Relevant automated checks, lint/type checks and production build.

Run checks once, repeating only where fixes require it. Do not weaken acceptance criteria to claim completion. Clearly distinguish passed checks, mocked failures and unverified behavior.

If the M3 gate passes, create:
- branch milestone/03-filing-intelligence
- annotated tag m3

Publication, commit-email decisions, permission hardening and M4–M5 remain deferred. Preserve my permission settings.

Finish with the running URL, exact restart commands, a three-minute M3 walkthrough, actual verification results, refs/commits and limitations. Then STOP and wait.

If I send the classroom freeze instruction, stop adding features, preserve unfinished work and run the latest verified milestone.
<!-- DISPATCH:END -->
