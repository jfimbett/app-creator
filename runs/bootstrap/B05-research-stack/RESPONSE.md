# RESPONSE — B05-research-stack

- From: default → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: 53107e3c-1e3d-4467-a8ac-5653a45d74c2 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T17:08:46.600Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I've written `docs/research/stack-versions.md`. Most of the D5/D6 pins hold, but Vitest breaks the D5 rule, the reason D5 gives for TypeScript is outdated, and this machine's Python is below the D6 floor.

**Pins that should change**
1. **Vitest 4.1.12 breaks the D5 rule.** Vitest 5.0.5 (released 2026-10-15) is the newest release at least two weeks old. I recommend moving to vitest 5.0.5 and raising the Node floor to 22.12. Vitest 5 needs Node 22.12 or later, and Playwright's docs already list only Node 22, 24 and 26 as supported. The alternative is to keep 4.1.12 and record that you are making an exception to support Node 20.
2. **TypeScript 6.0.3 is right, but for a different reason.** The Next.js docs now have a "Using TypeScript 7" section, so "avoided until Next documents support" no longer applies. The real blocker is lint: `eslint-config-next` depends on `typescript-eslint`, which only accepts TypeScript below 6.1.0. TypeScript 7 would break linting.
3. **D5 is missing pins:**
   - `@tailwindcss/postcss` 4.3.3 and `postcss` (the Tailwind v4 + Next.js setup needs them).
   - `react-is` 19.3.1 (Recharts needs it, and it must match the installed React).
   - `@types/react` / `@types/react-dom` and the Vitest helper packages. `vite` needs a separate pin at 8.x because `@vitejs/plugin-react` requires it.
   - The `shadcn` CLI.

All other D5/D6 pins pass the two-week rule. D6's Python 3.10–3.13 range is valid.

**Other things that affect implementation**
- **Lint:** Next 16 removed `next lint`, and `next build` no longer runs the linter. Use plain `eslint` with an `eslint.config.mjs`; the file has the exact config. eslint 10 needs Node 20.19 or 22.13 or later, which is stricter than Next's 20.9.
- **Turbopack** is now the default for both `next dev` and `next build`. A custom webpack config makes `next build` fail unless you pass `--webpack`.
- **shadcn** can run without prompts, so you can add components once and commit them. There is no `--base-color` flag. Its current default style is nova/base-nova, not new-york. The manual install now uses a `cn` package instead of clsx plus tailwind-merge.
- **Playwright** can use project-local browsers. Setting `PLAYWRIGHT_BROWSERS_PATH` for both install and test runs, with `install --only-shell chromium`, gives a small headless-only install. `webServer` accepts a list, so one config can start both FastAPI and `next start`.

## Handoff
Changes: `docs/research/stack-versions.md` (new). About 1,600 words counting URLs and code, so above the ~1,300 target; the prose itself is near the limit. No other files edited, nothing installed, no commit. The working tree also shows `runs/INDEX.md`, `docs/TOOLKIT.md` and `runs/bootstrap/B06-agents/` as changed; I didn't touch them.
Verification evidence: pages fetched on 2026-11-03:
- **Next.js:** nextjs.org/docs pages for installation, TypeScript config, rewrites, distDir, ESLint, Turbopack, the v16 upgrade guide, the CLI, and the Vitest testing guide.
- **Tailwind:** tailwindcss.com/docs/installation/framework-guides/nextjs.
- **shadcn:** ui.shadcn.com/docs pages for the Next.js install, Tailwind v4, the CLI, manual install and components.json.
- **Recharts:** recharts.github.io/en-US/guide/installation, plus the GitHub README and the 3.0 migration guide.
- **Playwright:** playwright.dev/docs pages for browsers, webServer and the intro.
- **FastAPI:** fastapi.tiangolo.com (home page and manual deployment).
- **Vitest:** vitest.dev/guide.
- **Metadata:** `npm view` (versions, release dates, engines, peers) and the PyPI JSON API for the D6 packages.

Failures:
- www.uvicorn.org didn't resolve (DNS error), so Uvicorn's own docs are marked [unverified]. Uvicorn details come from the FastAPI docs and PyPI instead.
- The rewrites page doesn't say whether rewrites behave differently under `next dev` and `next start` [unverified].
- No Recharts page says "React 19" in so many words; only its npm peers (`^19.0.0`) show support.

Remaining findings:
- **Contradicts D5:** the Vitest pin breaks D5's own rule, the TypeScript reason is outdated, and several pins are missing (listed above).
- **Fits D6:** FastAPI, Uvicorn, Pydantic and pytest require Python 3.10 or later and also list 3.14. httpx's listed versions stop at 3.12, so keeping 3.13 as the tested ceiling is sensible.
- **Local environment:** `python3` here is 3.9.19, below the 3.10 floor, and no newer Python is on PATH. Node is v22.14.0, which meets every requirement above.

Next action: decide between vitest 5.0.5 with a Node 22.12 floor or keeping 4.1.12 as a recorded exception, then update D5 with the corrected TypeScript reason and the missing pins, and tell the user to install Python 3.10 or later.
<!-- VERBATIM:END -->
