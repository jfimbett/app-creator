# M1 Foundation: follow-up prompts

This file records every follow-up prompt that changes this milestone's implementation after [PROMPT.md](PROMPT.md)
was dispatched (a repair, a correction or an extra instruction). Each one is appended here **with its exact text,
before it is dispatched**, together with its date, sender, receiver and the step record in `runs/` that it belongs
to. Entries are never edited or removed afterwards. PROMPT.md itself stays unchanged.

## 2026-11-04, instructor → top-level session, runs/recovery/R01-classroom-demo

Saved during the step, after its first fixes, not before it began: a deviation from this file's rule.

> URGENT CHANGE OF PRIORITY: my class starts in approximately 90 minutes. Suspend the full GOAL.md completion workflow. Deliver one working classroom demonstration first.
>
> The previous session appears stuck in a long-running shell command while modifying a review-dispatch script after m1-10. Do not retry that command or wait for old background tasks.
>
> First inspect Git status, PROGRESS.md, recent commits, existing application files, and relevant processes. Preserve all existing work. Identify whether any previous build agents are still modifying this repository; stop only those project-specific tasks before making competing edits. Do not kill unrelated processes.
>
> For this recovery, work directly in the main session. Do not dispatch nested Claude CLI sessions, parallel reviewers, or additional orchestration infrastructure.
>
> Within the first 10 minutes:
> - Determine what functionality is actually implemented.
> - Start the most complete existing application in offline/demo mode.
> - Give me its exact local URL and tell me what currently works.
>
> Then spend at most 35 additional minutes fixing only problems that prevent the classroom demonstration: startup, company selection/search, visible financial data, charts, navigation, and major layout failures. Use existing authentic fixtures. Clearly label unavailable functionality and fixture dates. Do not fabricate financial information.
>
> Verification for this emergency pass:
> - One browser journey through the features we will demonstrate.
> - Inspect one desktop screenshot.
> - Run only targeted tests for any consequential fixes.
> Do not run the full milestone matrix, repeat production builds without a reason, wait for four reviews, or polish the toolkit before the demo works.
>
> Preserve existing milestone refs. Do not invent completed milestones or claim M2–M5 exist. Additional milestones, extensive reviews, transcript cleanup, and publication can wait until after the class.
>
> Save the recovery prompt and result, checkpoint the working application, and update PROGRESS.md with deferred work.
>
> Finish by leaving the demo running and giving me:
> 1. The clickable local URL.
> 2. Exact restart commands.
> 3. A five-minute demonstration script using features actually verified.
> 4. Known limitations.
>
> If a command stalls, diagnose it rather than waiting indefinitely. Send concise progress updates as you work.

## 2026-11-04, instructor → top-level session, runs/m1/m1-16-complete-m1-main-session

Saved before work began. It replaces the planned steps m1-11 to m1-15.

> Change execution mode: complete ONE milestone at a time, then stop and report. Do not automatically start the next milestone.
>
> Start with M1:
> - Preserve the working demo at commit 2133bca.
> - Inspect the remaining M1 acceptance criteria and finish essential missing work.
> - Keep execution in the main session; avoid nested Claude CLI sessions and lengthy parallel review dispatches.
> - Run the relevant checks once. Fix meaningful failures without restarting the entire workflow.
> - Preserve exact prompts, follow-ups and final responses.
> - Create the M1 checkpoint and tag only if its required gate passes. Otherwise report precisely what remains.
> - Leave the application running and give me the URL, changes, test results, limitations, and a short demonstration script.
>
> Do not start M2. Stop after the M1 report and wait for my instruction.
