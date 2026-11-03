# RESPONSE — B09-root-docs

- From: docs-writer → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 4043dcb0-5fbd-4a07-9d48-db9fd1656f32 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:42:21.713Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I've written or updated all ten files. `npm run check-toolkit` passes with exit 0 (177 relative links in 78 files resolve, 0 failures), and the template-mode commands all exit 0.

- **`CLAUDE.md` and `AGENTS.md`** are short and generic, as asked. The rules now read the app's folders from `app-creator.config.json`, and settings live in the root `.env.example` (the old text pointed at `app/.env`).
- **`README.md`, `START-HERE.md` and `PROMPTS.md`** cover the two paths (inspect the milestones after the example is published; start a new app from `template`), both assistants, delegated mode and recorded steps. Cline is marked untested throughout. In `PROMPTS.md`, Claude Code prompts are marked "documented"; only the step dispatcher is marked "used".
- **`LICENSE`** is the standard MIT text, copyright 2026 the App Creator authors.

**Run by me on this branch with no app yet** (macOS, Node 22.14, Python 3.10): `npm ci`, `npm run setup`, `npm run dev`, `npm run demo`, `npm run create-app -- --dry-run` and `npm run verify`. The `verify` run copied the tiny starter app to a temporary folder, installed it, built it and ran the browser test; it passed.

**Not verified**, and labelled that way in the docs:
- cloning from the published repository;
- Path A (the milestone tags don't exist yet);
- a real `npm run create-app` followed by `npm run dev`;
- every slash-command prompt;
- everything in Cline.

**Things you need to decide or fix:**
1. **Node version:** the brief said 22.12 or newer, but `package.json` and `docs/TOOLKIT.md` say 22.13 (raised in commit b127968). I used 22.13 everywhere.
2. **License mismatch:** `package.json` still says `"license": "UNLICENSED"` while the new `LICENSE` is MIT. Only you can change `package.json`.
3. **Milestone prompts:** `milestones/` doesn't exist yet, so nothing links to it. Once the five build prompts are added, `README.md` and `START-HERE.md` should mention them.
4. **`runs/` on the template branch:** `AI-USAGE.md` and `PROMPTS.md` link to `runs/INDEX.md`. If `template` leaves out `runs/`, those links break.
5. **Commit prompts:** the docs say Claude asks before every commit. That only follows from `git commit` not being on the allow list in `.claude/settings.json`; I didn't watch the prompt appear.

## Handoff
Changes: CLAUDE.md, AGENTS.md, START-HERE.md, PROMPTS.md, AI-USAGE.md, .clinerules/cline.md, .clineignore, docs/README.md (changed); README.md, LICENSE (new).
Verification evidence: `npm run check-toolkit` exit 0 (33 ok, 3 warnings about skills with no extra guides, 0 failures; 177 links in 78 files). Template mode: `npm ci`, `npm run setup`, `npm run dev`, `npm run demo`, `npm run create-app -- --dry-run` all exit 0; `npm run verify` exit 0 (all checks passed, starter app checked in a temporary folder). Scans for placeholder text, emails, keys and personal paths in my files: no matches. Every file I linked exists (`ls`).
Remaining findings: Node 22.12 in the brief vs 22.13 in the code (used 22.13); `package.json` license is "UNLICENSED", should be MIT; `milestones/` not there yet, docs to mention it once added; `runs/` links break if `template` leaves it out; commit prompt not seen; clone, Path A, real create-app + dev, slash prompts and all Cline steps not verified.
Next action: Owner reviews and commits the B09 files, updates the `package.json` license field, and adds `milestones/` mentions once the five build prompts exist.
<!-- VERBATIM:END -->
