# PROMPT — R01-classroom-demo

- Sender: the instructor (owner of the repository), pasted into a resumed top-level session on 2026-11-04
- Receiver: top-level Claude Code session (Opus 5.5), working directly; no dispatched agents
- Starting commit: 646e32cdd16a1885d2890278a4d9becbb036da16
- Skills loaded: none. Instruction paths: AGENTS.md, examples/sec-analytics/CLAUDE.md

<!-- DISPATCH:BEGIN -->
URGENT CHANGE OF PRIORITY: my class starts in approximately 90 minutes. Suspend the full GOAL.md completion workflow. Deliver one working classroom demonstration first.

The previous session appears stuck in a long-running shell command while modifying a review-dispatch script after m1-10. Do not retry that command or wait for old background tasks.

First inspect Git status, PROGRESS.md, recent commits, existing application files, and relevant processes. Preserve all existing work. Identify whether any previous build agents are still modifying this repository; stop only those project-specific tasks before making competing edits. Do not kill unrelated processes.

For this recovery, work directly in the main session. Do not dispatch nested Claude CLI sessions, parallel reviewers, or additional orchestration infrastructure.

Within the first 10 minutes:
- Determine what functionality is actually implemented.
- Start the most complete existing application in offline/demo mode.
- Give me its exact local URL and tell me what currently works.

Then spend at most 35 additional minutes fixing only problems that prevent the classroom demonstration: startup, company selection/search, visible financial data, charts, navigation, and major layout failures. Use existing authentic fixtures. Clearly label unavailable functionality and fixture dates. Do not fabricate financial information.

Verification for this emergency pass:
- One browser journey through the features we will demonstrate.
- Inspect one desktop screenshot.
- Run only targeted tests for any consequential fixes.
Do not run the full milestone matrix, repeat production builds without a reason, wait for four reviews, or polish the toolkit before the demo works.

Preserve existing milestone refs. Do not invent completed milestones or claim M2–M5 exist. Additional milestones, extensive reviews, transcript cleanup, and publication can wait until after the class.

Save the recovery prompt and result, checkpoint the working application, and update PROGRESS.md with deferred work.

Finish by leaving the demo running and giving me:
1. The clickable local URL.
2. Exact restart commands.
3. A five-minute demonstration script using features actually verified.
4. Known limitations.

If a command stalls, diagnose it rather than waiting indefinitely. Send concise progress updates as you work.
<!-- DISPATCH:END -->
