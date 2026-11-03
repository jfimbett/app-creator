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

Filled in after the checkpoint.
