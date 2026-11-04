# PROMPT — m1-16-complete-m1-main-session

- Sender: the instructor (owner of the repository), pasted into the top-level session on 2026-11-04
- Receiver: top-level Claude Code session (Opus 5.5), working directly; no dispatched agents
- Starting commit: 2133bca
- Skills loaded: none at start. Instruction paths: AGENTS.md, examples/sec-analytics/CLAUDE.md, milestones/01-foundation/PROMPT.md at template-v1
- Replaces the remaining dispatched steps in the M1 plan (runs/m1/m1-01-plan): m1-11 to m1-15

<!-- DISPATCH:BEGIN -->
Change execution mode: complete ONE milestone at a time, then stop and report. Do not automatically start the next milestone.

Start with M1:
- Preserve the working demo at commit 2133bca.
- Inspect the remaining M1 acceptance criteria and finish essential missing work.
- Keep execution in the main session; avoid nested Claude CLI sessions and lengthy parallel review dispatches.
- Run the relevant checks once. Fix meaningful failures without restarting the entire workflow.
- Preserve exact prompts, follow-ups and final responses.
- Create the M1 checkpoint and tag only if its required gate passes. Otherwise report precisely what remains.
- Leave the application running and give me the URL, changes, test results, limitations, and a short demonstration script.

Do not start M2. Stop after the M1 report and wait for my instruction.
<!-- DISPATCH:END -->
