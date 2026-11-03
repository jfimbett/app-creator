# PROMPT — B05-research-stack

- Sender: owner (top-level Claude Code session)
- Receiver: default Claude Code agent (`--agent default`; the toolkit's agents do not exist yet — orchestrator B01 risk 4)
- Starting commit: 10e8c6f
- Skills: none; instruction paths: GOAL.md, PROGRESS.md
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B05-research-stack --agent default --mode bypassPermissions --milestone bootstrap`
- Plan reference: runs/bootstrap/B01-orchestrator-bootstrap-plan/RESPONSE.md

<!-- DISPATCH:BEGIN -->
Research task for the App Creator build (see GOAL.md §4). Topic: verify the version pins recorded in PROGRESS.md decisions D5 and D6 against official documentation and package metadata. Check: (1) Next.js 16 docs (nextjs.org/docs): supported TypeScript versions (is TypeScript 6.x OK? TypeScript 7?), minimum Node, `rewrites` for proxying /api/* to a local backend in dev and in `next start`, `distDir`, how `next lint` changed (ESLint flat config, eslint-config-next), Turbopack default; (2) Tailwind CSS v4 setup with Next.js (@tailwindcss/postcss), and shadcn/ui's current Next.js + Tailwind v4 install (ui.shadcn.com/docs) — whether components can be added without the interactive CLI; (3) Recharts 3 with React 19; (4) Playwright: PLAYWRIGHT_BROWSERS_PATH for a project-local browser, `npx playwright install chromium` (and --only-shell / chromium-headless-shell), webServer config; (5) FastAPI current docs: supported Python versions; uvicorn; (6) Vitest 4 basics with React if useful. Use npm view / PyPI JSON for metadata where docs are silent. Report any pin that should change and why.
Rules: use only official documentation (fetch the pages; do not answer from memory), cite every claim with its URL and the retrieval date 2026-11-03, and mark anything you could not fetch as [unverified]. Write ONLY the one file named below (create docs/research/ if needed); do not edit any other file, do not install anything, do not commit. Keep the file under about 1300 words, as practical implementation notes. Never print or write secrets or email addresses. End your final message with:
## Handoff
Changes: <file written>
Verification evidence: <pages fetched (URLs) and any failures>
Remaining findings: <surprises, contradictions with the notes in PROGRESS.md decisions D5/D6>
Next action: <one line>
File: docs/research/stack-versions.md

<!-- DISPATCH:END -->
