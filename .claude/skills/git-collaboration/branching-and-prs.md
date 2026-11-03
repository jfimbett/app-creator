# Branches, commits and pull requests

Part of [git-collaboration](SKILL.md). Commands marked **(owner)** publish something and need the owner.

## Clone, fork, origin and upstream

| Word | Meaning |
|---|---|
| **clone** | a full copy of a repository on your computer: `git clone <url>` |
| **fork** | your own copy of someone else's repository *on GitHub*. Use it when you cannot push to the original (an instructor's template, an open-source project) |
| **origin** | the remote your clone came from. After cloning a fork, `origin` is your fork |
| **upstream** | by convention, the original repository you forked from. You add it yourself |

Team repository (everyone is a collaborator): clone it; `origin` is the shared repository; no fork needed.

Fork workflow (you cannot push to the original):

```bash
git clone <url-of-your-fork>
cd <repo>
git remote add upstream <url-of-original>     # local config only
git remote -v                                  # check: origin = your fork, upstream = original
git fetch upstream                             # download only
git switch main
git merge --ff-only upstream/main              # bring your main up to date (fails safely if diverged)
git push origin main                           # (owner) update your fork
```

Never point `origin` somewhere else without the owner; never push to `upstream`.

## Branches

```bash
git switch main
git pull --ff-only                 # update main; refuses if your main diverged (then ask)
git switch -c feat/csv-export      # new branch from main
git branch -vv                     # which branches exist and what they track
```

Naming: `<type>/<short-slug>`, type = `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `exercise`. One branch
per slice of `plan.md`. Keep it short-lived (one to three days); long branches mean big conflicts.

Keep your branch current with `main` while you work (by merging, see
[conflicts-merge-rebase.md](conflicts-merge-rebase.md)):

```bash
git fetch origin
git merge origin/main              # on your feature branch; resolve conflicts if any; run npm run verify
```

## Small commits with good messages

A good commit is one idea that still passes the checks. Checklist before each commit:

- [ ] `npm run verify` (or at least the slice's tests) passed.
- [ ] `git status` reviewed; only intended files.
- [ ] Staged by name: `git add app/backend/app/export.py app/backend/tests/test_export.py`.
- [ ] `git diff --staged` read once. No `.env`, keys, `node_modules/`, `.venv/`, `.cache/`, screenshots.
- [ ] Message: `<type>: <what changed, imperative, under ~70 chars>`, optional body explaining *why*.

```text
feat: export the results table as CSV

Users asked to open results in a spreadsheet. Missing values are written
as empty cells, not 0, so totals in the spreadsheet stay correct.
```

Fixing the last *unpushed* commit is fine: `git commit --amend` (local). Once pushed, make a new commit instead.

## Pull requests (PRs)

A pull request asks to merge your branch into `main` and gives teammates a place to review.

1. Prepare locally: branch up to date with `origin/main`, `npm run verify` passing, commits clean.
2. **(owner)** `git push -u origin feat/csv-export`.
3. **(owner)** Open the PR on GitHub or with `gh pr create --base main --title "feat: CSV export" --body-file pr.md`.

PR description template (the assistant can write `pr.md` text; it is not committed unless asked):

```markdown
## What
Adds a "Download CSV" button to the results table (slice 4 in plan.md, criteria A4.1–A4.3).

## Why
Users want the data in a spreadsheet.

## How to check
1. `npm run setup && npm run demo`
2. Open http://localhost:3000/results, click "Download CSV".
3. Open the file: 12 rows, empty cells where the table shows "—".

## Evidence
- `npm run verify`: exit 0 (backend 18 passed, frontend 9 passed, Playwright smoke passed)
- Screenshots looked at: 1366 px and 390 px

## Not done / risks
- Large tables (> 10 000 rows) not tested.

Closes #12
```

Keep PRs small: under ~400 changed lines and one topic. Split otherwise.

## Code review

Reviewer checklist (a teammate, or the `review-changes` skill's reviewer agents):

- [ ] I ran it: checked out the branch (`gh pr checkout 12` or `git fetch origin && git switch feat/csv-export`),
      `npm run setup`, `npm run verify`, followed "How to check".
- [ ] It does what the PR says, and only that (no unrequested scope).
- [ ] Tests cover the risky part (calculations, data, permissions) with independently known expected values.
- [ ] Names are clear; no dead code; no secrets; no personal data in fixtures.
- [ ] Docs updated if setup, commands or behaviour changed.

Comment style: specific and kind. "Line 42: an empty list makes `max()` raise; can we show the empty state?"
beats "this is wrong". Mark comments as **blocking** or **suggestion**. Approve only what you ran.

Author: answer every comment (fix in a new commit, or explain), push again (owner), re-request review. Do not
force-push during review; reviewers lose their place.

Merging: **(owner or the agreed maintainer)** after approval and green checks. For teams, prefer
**squash and merge** (one tidy commit per PR on `main`) or a merge commit. Then delete the remote branch on
GitHub and locally `git switch main && git pull --ff-only && git branch -d feat/csv-export`
(`-d` refuses to delete unmerged work, which is what you want).
