# M3 Filing intelligence: follow-up prompts

This file records every follow-up prompt that changes this milestone's implementation after [PROMPT.md](PROMPT.md)
was dispatched (a repair, a correction or an extra instruction). Each one is appended here **with its exact text,
before it is dispatched**, together with its date, sender, receiver and the step record in `runs/` that it belongs
to. Entries are never edited or removed afterwards. PROMPT.md itself stays unchanged.

## F1 — 2026-11-04 — main-session execution instruction

- Sender: the instructor. Receiver: top-level Claude Code session. Record: `runs/m3/m3-02-implement-main-session/`.
- Exact text (home directory name replaced by an explicit marker):

```text
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
```

## F2 — 2026-11-04 — classroom freeze

- Sender: the instructor. Receiver: top-level Claude Code session. Record: `runs/m3/m3-03-classroom-freeze/`.
- It stopped M3 before its gate. Exact text:

```text
CLASSROOM FREEZE — conclude now with the work already implemented.

Stop adding features and stop launching additional test suites, repeated builds or review agents. Inspect the currently running command: let a short, progressing check finish, but interrupt a stalled or lengthy check safely. Preserve all existing work.

1. SELECT THE CLASSROOM VERSION

Determine the actual M3 implementation and verification status from existing evidence.

- If M3 has passed its required checks, checkpoint it as m3 and milestone/03-filing-intelligence.
- If it has not, preserve it on a clearly named work-in-progress branch. Do not label it verified. Use verified M2 as the classroom default.
- Do not discard unfinished work or move existing verified tags.
- Run only one short smoke check if needed to establish that the selected classroom version starts and its main journey works.
- Leave that version running on frontend port 3200 and backend port 8200. Do not stop unrelated services.

2. FINALIZE THE STUDENT HANDOFF

Create CLASSROOM.md on main containing:
- What students need installed.
- Exact clone and setup commands using the actual repository URL.
- The available milestone tags and corresponding branches.
- Exact commands to stop the app, switch milestones safely, update dependencies and restart.
- Plain-language prompts students can give Claude Code to perform those operations.
- Default offline/demo instructions, with Live mode clearly separated and local SEC identification explained.
- A short demonstration of each completed milestone and its limitations.
- Exact links to the recorded milestone prompts, follow-ups and detailed execution records.
- A clear explanation that inspecting a milestone uses its completed tag, whereas rebuilding it starts from the previous milestone.

Make main contain the latest verified classroom implementation plus final documentation. Preserve any unverified M3 implementation separately. State explicitly whether main contains M2 or M3 functionality.

Create a readable milestone/prompt index. For every completed milestone, link:
- The original milestone PROMPT.md.
- FOLLOWUPS.md, if present.
- Actual implementation prompts and available final responses under runs/.
- A short description of what changed.

Do not invent missing transcripts. Mark known gaps. Do not claim the original brief alone contains all the instructions actually used.

3. PUBLISH TO GITHUB NOW

Publication of the NEW PUBLIC app-creator repository under my authenticated personal GitHub account is authorized. No cloud deployment.

Check the actual authenticated owner and remote state first:
- If no repository exists, create it and configure origin.
- If the intended repository already exists and is demonstrably this project's remote, update it normally.
- Do not overwrite an unrelated repository or force-push.

Before pushing, perform the necessary focused secret/privacy review of files AND reachable history:
- Never publish .env, API keys, tokens, local SEC contact configuration or private logs.
- Use my GitHub noreply address for new commits.
- If my Gmail occurs only in commit author/committer metadata, I authorize publishing that existing metadata for this classroom release; do not spend time rewriting history solely for the author email.
- That permission does not authorize publishing credentials or private contact configuration in file contents.
- Preserve my current permission settings; optional permission hardening is deferred.

Push main, template, all completed milestone branches and their tags using explicit refs. Publish any preserved M3 work-in-progress branch only after the same secret review and with a clear unfinished label. Do not push unrelated branches or backup refs.

Verify the remote refs match the intended local commits. Confirm students can access the public repository. If publication genuinely fails, report the exact blocker and provide a clean classroom ZIP excluding secrets, caches, dependencies and local configuration as a fallback.

4. FINAL RESPONSE — GIVE ME THE CLASSROOM HANDOFF

Lead with:
- The actual clickable GitHub repository URL.
- The running local app URL.
- “Main currently contains M2” or “Main currently contains M3”, with any documentation-only commits explained.

Then provide:
A. A small table of available versions: functionality, branch, tag, commit and verification status.
B. Exact student commands to clone, install and run.
C. Exact commands AND plain-language Claude prompts to switch between the completed milestones without losing student edits.
D. Clickable GitHub links to each milestone's prompts, follow-ups and execution index.
E. A five-minute instructor walkthrough.
F. Known limitations and any publication or transcript gaps.

Use the actual launch scripts and ports; do not copy unverified commands from earlier messages. Do not claim GitHub CI passed unless it actually did.

Update PROGRESS.md with deferred work. Then STOP. Do not start another implementation or verification cycle.
```

## Follow-up 4 (2026-11-09): finish M3

Typed by the instructor in a new session on Windows 11, after the assistant had reported the project status. Recorded in
[runs/m3/m3-04-finish-main-session/PROMPT.md](../../runs/m3/m3-04-finish-main-session/PROMPT.md) before any implementation
work. It is appended here afterwards, at the checkpoint.

```text
continue m3 as you think is better, work autonomously only let me know when m3 is done
```
