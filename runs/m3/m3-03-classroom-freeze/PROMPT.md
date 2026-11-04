# PROMPT — m3-03-classroom-freeze

- Sender: the instructor (owner of the repository), pasted into the top-level session on 2026-11-04, interrupting M3 implementation
- Receiver: top-level Claude Code session (Opus 5.5), working directly; no dispatched agents
- Text below is exact.

<!-- DISPATCH:BEGIN -->
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
<!-- DISPATCH:END -->
