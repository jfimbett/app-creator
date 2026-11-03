# RESPONSE — B13-milestone-prompts

- From: product-architect → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 7201d280-399d-4fed-8070-c50925e339f9 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:07:01.830Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I've written all 15 files: one build prompt per milestone, each with the 12 required sections, plus a README and an empty FOLLOWUPS.md in each folder. `npm run check-toolkit` passes (34 ok, 3 warnings, 0 failures).

**What each prompt specifies:**
- **Starting ref:** the exact tag and the student command (`git switch -c exercise/build-mN <ref>`), with a note that the finished `mN` checkout is for inspection only.
- **Context:** a summary of what the start ref contains. For M2–M5 this is the planned result of the earlier milestones, so each prompt tells the implementer to trust the actual code if it differs and record the difference.
- **Files and contracts:** the full file layout, API shapes, fixture rules, the SEC and AI rules that apply at that milestone, named pytest/Vitest/Playwright cases, the gate, the acceptance checklist, out-of-scope items, and the Handoff block with "do not commit, tag or push".
- **M1 setup:** creating `examples/sec-analytics`, the config entry, the example `CLAUDE.md`, the nested `sec-edgar-data` skill (with the note that Claude Code loads it the first time a file in that folder is touched), the `sec-data-specialist` agent, and the fixture capture script with its manifest. The script never invents or records the contact value.
- **M5:** covers every item in your list (key handling, models and pricing, limits, cancel, error mapping, grounding and citations, and the required tests). Live AI is reported as "not verified (N1)" unless the owner explicitly authorizes a test key.

No email addresses appear in any of these files. All example numbers and dates are placeholders. The Microsoft and Alphabet CIKs come from memory, so the M1 capture script must check them against SEC's ticker file and stop if they differ.

**Decisions you should know about:**
- **Screenshot widths:** your brief says 1366 and 390 px; the recorded decision (Q14, M1-AC6) says 1440 and 390. The prompts require all three widths.
- **Filing documents:** plan slice 1.2 and decision Q20 put 10-K/10-Q excerpts in M1. I followed your brief instead: M3 adds the full primary documents, gzip-compressed, read from the existing snapshot. `plan.md` slice 1.2 and the fixture path in `architecture.md` now need updating.
- **M2 explorer chart:** M2-AC5 says "a line chart shows both series" (net margin in % and FCF in USD). To avoid putting two units on one axis, the prompt asks for stacked small charts with a shared year axis. Please confirm.
- **M4 CSV:** I read "exactly the rows shown" as "exactly the data points shown": the table is wide, the CSV has one line per data point, in the same order.
- **API additions:** the prompts introduce new error codes and fields. Examples are `sec_refused`, `document_not_in_snapshot`, `forbidden_origin` and `document_in_snapshot`. Each implementer is told to add them to `architecture.md`, which I did not edit.
- **Settings reader:** the prompts use a plain pydantic model that reads the environment, not the `pydantic-settings` package that `architecture.md`'s wording implies, to avoid a new dependency.
- **Example agent:** M1 adds `.claude/agents/sec-data-specialist.md`, even though `plan.md` says not to touch `.claude/`. Your brief and TOOLKIT §1 allow it.

**Things that changed under me:**
- While I worked, a parallel step (B16) modified `docs/TOOLKIT.md`, `scripts/create-app.mjs` and other scripts. The new TOOLKIT §3 says only `npm run dev` and `setup` pass the root `.env` to child processes, so I corrected M1's context to match. The B13 record's file hashes (`runs/bootstrap/B13-milestone-prompts/PROMPT.md`) were taken before these edits and are now out of date.
- `milestones/README.md` still says the milestone folders "are added in the next bootstrap step". That is now stale; I left it alone because it was outside my file list.

## Handoff
Changes: created `milestones/0{1..5}-*/PROMPT.md`, `README.md` and `FOLLOWUPS.md` (15 files); no other files edited.
Verification evidence: `npm run check-toolkit` → 34 ok, 3 warnings (pre-existing: skills without guides), 0 failures, exit 0 (markdown links resolve; 5 milestone prompts found); email-address grep over the five folders → no matches (exit 1).
Remaining findings: width mismatch handled by requiring 1440, 1366 and 390 px; filing documents moved from M1 (plan 1.2, Q20) to M3 per the brief, so `plan.md` and `architecture.md` need updating; M2-AC5 and M4-AC6 interpretations need owner confirmation; implementers must record the additive API codes and fields in `architecture.md`; `milestones/README.md` is stale; B16 edited toolkit files during this step, so the B13 record's hashes are out of date; N1 and N2 remain open.
Next action: owner reviews the decisions above, then integrates and commits the prompts before creating `template-v1`.
<!-- VERBATIM:END -->
