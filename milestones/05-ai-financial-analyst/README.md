# M5 AI financial analyst

**What it delivers.** On top of the earlier milestones, SEC Analytics adds an optional analyst panel on the company, filing and comparison screens. You add your own OpenRouter key (kept in memory unless you opt in to this tab's sessionStorage), pick a model from the live list with its prices, and ask questions. Answers are grounded in the app's own computed numbers and filing passages and cite server-assigned source ids that the app checks. Everything else works without a key.

The AI part is tested with a mocked OpenRouter. Unless the Results below say otherwise, **live AI is not verified** (no authorized test key was available, decision N1 in [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md)).

## Inspect it at its tag

From a clean checkout (stop any running `npm run dev` or `npm run demo` and check `git status` first):

```bash
git fetch origin --tags
git switch --detach m5
npm ci
npm run setup
npm run demo
```

Open http://127.0.0.1:3000. Without a key, check that every earlier screen still works and the panel says "AI not configured". With your own limited key (this part needs the network): test the connection (it may cost a little), choose a model, and ask "Why did net margin change?" on Apple. `npm run demo` needs no keys and no network. The tag also has a branch,
`milestone/05-ai-financial-analyst`.

## Rebuild it (exercise)

Start from the previous milestone's tag, `m4`, on a new branch, and give the assistant [PROMPT.md](PROMPT.md):

```bash
git switch -c exercise/build-m5 m4
```

The `m5` checkout is for inspection, not for re-running its own prompt. Your result will differ from `m5`:
replaying a prompt does not reproduce the same code. The tag is the reference version.

## Files

- [PROMPT.md](PROMPT.md): the exact build brief used for this milestone (unchanged after `template-v1`).
- [FOLLOWUPS.md](FOLLOWUPS.md): any implementation-changing follow-up prompts, saved before they were sent.
- Shared planning: [product](../product.md), [architecture](../architecture.md), [acceptance](../acceptance.md),
  [plan](../plan.md).

## Results

**Added.** An **Analyst** button on the company page, the filing reader and Compare opens a panel (beside the page on wide
screens, full screen on a phone). Without a key it says "AI not configured: add your own OpenRouter key" and the rest of the
app works as before. **AI settings** takes the person's own OpenRouter key (masked; memory only, or this tab after a warned
opt-in; never localStorage), lists models with prices per million tokens and expiry dates (none preselected; a manual id is
allowed), warns "This may incur a small charge" before the connection test, and clears the key. A question gets a plain-text
answer with numbered source chips for the app's own facts and filing passages, invalid references listed, and the notice
"Source links are checked; the claims themselves may still be wrong." The backend keeps the key only for the one upstream
call, refuses foreign origins and hosts, limits size, context and concurrency, never retries, cancels on Cancel, and refuses
price, valuation, advice and unloaded-company questions before any model call.

**Checked.** `npm run verify` with no key (pytest with a mocked OpenRouter, Vitest, lint, types, build, Playwright including 13
M5 journeys with a mocked backend and screenshots at 1440, 1366 and 390 px), the screenshots looked at, the real context line
on all three screens with no key, cancel through the Next.js proxy with a slow fake client, and independent security
(backend and frontend) and test reviews whose findings were fixed. Exact results:
[runs/m5/m5-01-implement-main-session/RESULT.json](../../runs/m5/m5-01-implement-main-session/RESULT.json).

**Live AI: not verified (N1).** No authorized, limited test key was available, so no real model was called. M5-AC9 stays
`blocked: N1` until the owner runs one connection test and one chat with such a key.

**Limitations.** Answers can be wrong even when every source chip is valid. The context is the latest five fiscal years and at
most 8 passages. The scope pre-check is deliberately simple: it misses a one-word company name written in lower case.
