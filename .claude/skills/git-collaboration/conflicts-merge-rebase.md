# Conflicts, merge versus rebase, and recovery

Part of [git-collaboration](SKILL.md). Everything here is local unless marked **(owner)**.

## Resolving a merge conflict step by step

A conflict happens when two branches changed the same lines. Git stops and asks you to choose.

1. **Start from a clean state and a passing build.** `git status` clean; `npm run verify` passing on your branch.
2. **Bring in the other side:**
   ```bash
   git fetch origin
   git merge origin/main
   ```
   Git prints `CONFLICT (content): Merge conflict in app/frontend/src/lib/format.ts`.
3. **List the conflicted files:** `git status` (section "Unmerged paths") or `git diff --name-only --diff-filter=U`.
4. **Read the markers** in each file:
   ```text
   <<<<<<< HEAD
   export const formatNumber = (n: number) => n.toFixed(2);
   =======
   export const formatNumber = (n: number | null) => (n === null ? "—" : n.toFixed(1));
   >>>>>>> origin/main
   ```
   Top (`HEAD`) = your branch. Bottom = the incoming branch. You may keep one, the other, or combine both.
   Here the combined answer keeps `main`'s null handling (missing is not zero) and your two decimals:
   ```ts
   export const formatNumber = (n: number | null) => (n === null ? "—" : n.toFixed(2));
   ```
5. **Remove every marker**, then check none remain: `git diff --check` and `grep -rn '<<<<<<<\|>>>>>>>' app/`.
6. **Lockfiles** (`package-lock.json`, `requirements.lock`): do not hand-edit. Take one side
   (`git checkout --theirs package-lock.json`), then regenerate with the dependency tool (for npm: `npm install`
   in that folder) and rerun `npm run setup`.
7. **Test the result:** `npm run verify`. A merge that compiles is not proof; the tests and the journey are.
8. **Finish:** `git add <each resolved file>` then `git commit` (git proposes a merge message; keep it).
9. **Not sure? Back out safely:** `git merge --abort` returns to exactly where you were before step 2.

Ask the author of the other side when a conflict is in logic you do not understand. Two minutes of talking beats
silently dropping a teammate's fix.

## Merge versus rebase

| | Merge (`git merge origin/main`) | Rebase (`git rebase origin/main`) |
|---|---|---|
| What it does | adds a merge commit joining the two histories | replays your commits on top of the other branch, creating *new* commits |
| History | true record, some extra merge commits | linear, but rewritten |
| Safe on pushed/shared branches? | **yes** | **no**: teammates' copies no longer match; needs a force-push |
| Conflicts | resolved once | may be resolved once per replayed commit |

**Team rule:** merge `main` into your feature branch to update it; merge PRs with **squash and merge** or a merge
commit. Rebase only a private branch nobody else has fetched, and never `main`. If you started a rebase and are
lost: `git rebase --abort`.

Never `git push --force` to a shared branch. If an owner decides a force-push on their *own* unshared branch is
needed, use `git push --force-with-lease` **(owner)**, which refuses if someone else pushed meanwhile.

## Recovery without destructive commands

First rule: **save before you fix.** Put the current state on a rescue branch; branches are free.

```bash
git switch -c rescue/2026-11-03     # everything committed so far is now also here
git status
```

| Situation | Safe command | Undo |
|---|---|---|
| Changed a file and want the committed version back (discards *that file's* edits; check first with `git diff <file>`) | `git restore <file>` | none for the discarded edits, so stash first if unsure: `git stash push <file>` |
| Staged a file by mistake | `git restore --staged <file>` | `git add <file>` |
| Bad commit not pushed yet, just the message | `git commit --amend` | `git reflog` shows the previous commit |
| Bad commit already pushed | `git revert <sha>` (a new commit that undoes it) | `git revert <revert-sha>` |
| Committed on `main` instead of a branch (not pushed) | `git switch -c feat/x` (the work is now on `feat/x`); then ask the owner how to move `main` back | — |
| Merge or rebase going wrong | `git merge --abort` / `git rebase --abort` | — |
| Need to put work aside | `git stash push -m "wip: chart"` | `git stash pop` |
| "I lost a commit" | `git reflog` lists where `HEAD` was; `git switch -c rescue/found <sha>` | — |
| Untracked junk files | list them: `git clean -n` (dry run only) and delete specific files by hand | — |

**Not default advice:** `git reset --hard`, `git clean -fd`, `git push --force`, `git checkout -- .`,
`git branch -D`, deleting or moving tags. They delete work or rewrite shared history. If one is truly needed,
say exactly what will be lost, make a rescue branch or copy first, and let the owner decide.

## Committed a secret?

1. Tell the owner immediately; the owner **revokes/rotates the key** at the provider. This is the fix.
2. Remove it from the code and `.env.example`, commit the removal.
3. History rewriting to purge it is an owner decision and does not un-leak a pushed key.
