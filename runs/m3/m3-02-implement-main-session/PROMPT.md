# PROMPT — m3-02-implement-main-session

- Sender: the instructor (owner of the repository), pasted into a fresh top-level session on 2026-11-04 after `/clear`
- Receiver: top-level Claude Code session (Opus 5.5), working directly; no dispatched agents
- Starting commit: 6880338 on main and work/m3 (descends from tag m2, 4451d43; only records added after the tag)
- Workspace: isolated worktree `.worktrees/m3`, branch `work/m3`; the classroom M2 app keeps running from the main checkout
- Milestone brief: `milestones/03-filing-intelligence/PROMPT.md`, unchanged since `template-v1`
- Supersedes: `runs/m3/m3-01-implement-main-session/PROMPT.md`, which was saved but never executed
- Text below is exact, except that the home directory name is replaced by an explicit `[REDACTED:user]` marker.

<!-- DISPATCH:BEGIN -->
This is a fresh context. First read PROGRESS.md, CLAUDE.md and applicable project instructions. Then execute the assignment below.

Proceed with M3 — Filing Intelligence ONLY. M4–M5 and GitHub publication are deferred until after class.

CURRENT STATE
- Project: /Users/[REDACTED:user]/Documents/app-creator
- M2 passed its gate at tag m2, commit 4451d43.
- Main contains additional execution records; inspect its actual current state.
- The classroom app runs at http://127.0.0.1:3200, with backend port 8200.
- M2 supports live SEC data and recorded offline demo data.
- Preserve m1/m2 tags, existing records, local configuration and my permission settings.
- Do not restore the starter's Ask rules for commits or pushes.
- Read the saved handoff for any newer information.

Read GOAL.md, the recorded M3 prompt, the agreed product documents and current architecture. Record this exact instruction before implementation. If this instruction changes the original execution plan, document the deviation.

DELIVER M3

1. Company filing history for 10-K and 10-Q reports:
   - Form type.
   - Filing date.
   - Reporting period.
   - Accession number.
   - Amendment labels for 10-K/A and 10-Q/A.

2. Open the latest available annual or quarterly report:
   - Distinguish original reports from amendments.
   - Do not silently substitute an amendment for the original report.
   - Provide links to the original SEC documents.

3. Read actual filing text inside the application:
   - Readable typography and layout.
   - Loading, unavailable-document and error states.
   - Text search with visible matches and navigation between matches.
   - Navigation through detected sections.
   - Clearly labelled fallback when reliable section extraction is unavailable.

DATA AND SECURITY

Use the existing backend SEC client, identifying User-Agent, cache, throttling, timeouts and error handling. Reuse the locally configured contact information without printing it or committing it.

Fetch the primary filing document from validated SEC archive URLs. Validate redirects and paths. Do not create an arbitrary URL proxy.

Treat filing content as untrusted. Render sanitized text without executing embedded scripts or active HTML.

Live mode must retrieve actual SEC filing history and documents. Show retrieval dates and whether content is live or cached.

Preserve offline classroom mode using compact, authentic recorded filings or excerpts with source URLs, snapshot dates and explicit scope labels. Never present an excerpt as a full filing or a recorded document as the latest live report.

Do not fabricate filing text, dates, sections or sources.

PRIORITIES

Prioritize:
1. Filing history.
2. Opening and reading a document.
3. Searching its text.
4. Useful section navigation.

Implement robust fallbacks before sophisticated section extraction. Do not add AI summaries, comparisons or other M4/M5 features.

EXECUTION

Work directly in this session using relevant skills. Resolve routine product questions from GOAL.md and the saved decisions; do not restart an interview.

Avoid nested Claude CLI processes, parallel review-dispatch scripts and unrelated toolkit changes. Use short shell commands. Diagnose stalled commands rather than waiting indefinitely.

Preserve the running, verified M2 classroom application on ports 3200/8200. Implement and verify M3 in an isolated worktree with separate ports. Keep its configuration local and untracked. Do not modify the checkout underneath the running M2 application or stop unrelated services.

Once M3 passes verification, deliberately switch the classroom app to the verified M3 version. If M3 is blocked, leave M2 available.

RECORDS

Preserve the exact milestone prompt, implementation instructions and follow-ups. Save actual final task responses where accessible, test commands/results, evidence paths and relevant commits.

Keep the records honest: mark transcript-capture gaps explicitly, and do not reconstruct messages as if they were verbatim originals. Do not spend classroom preparation time repairing historical transcript gaps.

VERIFICATION

Check:
- M1/M2 functionality remains working.
- Filing metadata, dates, source links and amendment handling.
- Actual document retrieval and readable text.
- Search and section navigation/fallback.
- Sanitization, invalid paths and unavailable documents.
- At least one successful live SEC filing retrieval.
- Offline filing access without SEC network requests.
- One complete browser journey and desktop visual inspection.
- Relevant automated tests, lint/type checks and production build.

Run checks once, repeating only where fixes justify it. Clearly distinguish fixture tests, mocked failures and successful live checks. Do not weaken acceptance criteria or claim an unverified feature is complete.

CHECKPOINT

If M3 passes its applicable gate:
- Commit the verified implementation.
- Create branch milestone/03-filing-intelligence.
- Create annotated tag m3.
- Confirm m2 is an ancestor and leave m1/m2 unchanged.
- Update PROGRESS.md, milestone documentation and execution records.

If it does not pass, preserve partial work separately and report precisely what remains. Do not label it a verified m3 release.

FINISH

Leave the latest verified application running and report:
1. Clickable local URL and exact restart commands.
2. What M3 adds.
3. A three-minute classroom walkthrough.
4. Actual test results, including live SEC verification.
5. Branch/tag and commit references.
6. Limitations and blockers.

Then STOP. Do not begin M4, M5 or publication.

If I send a classroom freeze instruction, stop adding features, preserve unfinished work and run the latest verified milestone.
<!-- DISPATCH:END -->
