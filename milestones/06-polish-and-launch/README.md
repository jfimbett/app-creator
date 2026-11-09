# M6 Polish and launch

**What it delivers.** SEC Analytics gets a visibly more polished, consistent interface in a **dark and a light theme**
(toggle in every header; dark stays the default), a **landing page** at `/` that explains the product, and a short
**launch video**. The app itself moves to `/app`; every other URL is unchanged. The landing page has fictional
testimonials, illustrative pricing and a fictional company story, each **labelled as fictional or illustrative where
it appears** (owner decisions O1–O6 in [docs/PRODUCT-DECISIONS.md](../../docs/PRODUCT-DECISIONS.md)). There are still
no accounts, no payments and no sign-up. Everything works offline in Demo mode with no key.

## Inspect it at its tag

From a clean checkout (stop any running `npm run dev` or `npm run demo` and check `git status` first):

```bash
git fetch origin --tags
git switch --detach m6
npm ci
npm run setup
npm run demo
```

Open http://127.0.0.1:3000 for the landing page, then **Open the app** (http://127.0.0.1:3000/app). Use the sun/moon
button in the header to switch themes; reload and the choice stays. The video is
[`examples/sec-analytics/brag-output/brag.mp4`](../../examples/sec-analytics/brag-output/brag.mp4). `npm run demo` needs
no keys and no network. The tag also has a branch, `milestone/06-polish-and-launch`.

## Rebuild it (exercise)

Start from the previous milestone's tag, `m5`, on a new branch, and give the assistant [PROMPT.md](PROMPT.md):

```bash
git switch -c exercise/build-m6 m5
```

The `m6` checkout is for inspection, not for re-running its own prompt. Your result will differ from `m6`:
replaying a prompt does not reproduce the same code. The tag is the reference version.

## Files

- [PROMPT.md](PROMPT.md): the exact build brief used for this milestone.
- [FOLLOWUPS.md](FOLLOWUPS.md): the start instruction and the one correction the brief asked to record (the M5
  localStorage assertions).
- Shared planning: [product](../product.md), [architecture](../architecture.md), [acceptance](../acceptance.md),
  [plan](../plan.md).

## Results

Left for the owner: after watching the video and looking at both themes, write here what you think worked and what
you would change. The assistant's checks are in
[runs/m6/m6-01-implement-main-session/RESULT.json](../../runs/m6/m6-01-implement-main-session/RESULT.json).
