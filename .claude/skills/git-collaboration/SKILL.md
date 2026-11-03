---
name: git-collaboration
description: Use when someone asks how to branch, commit, open or review a pull request, resolve a merge conflict, choose merge or rebase, tag a release, use Issues or Projects, set up a team of about five, switch versions safely, or recover from a messy git state without losing work.
---

# Work safely with git and GitHub, alone or in a team

Git is the tool that records versions of the project on your computer. GitHub is a website that stores a copy
of the repository (the project folder with its full history) so a team can share it, review changes and track work.
This skill keeps both safe: small checkpoints, reviewed merges, nothing lost, and nothing published without the
owner.

## The one distinction that matters: local versus publication

| Kind | Examples | Who may do it |
|---|---|---|
| **Read-only** (changes nothing) | `git status`, `git log`, `git diff`, `git branch -vv`, `git remote -v`, `git stash list`, `gh pr list`, `gh pr view` | anyone, any time |
| **Local** (changes only your computer, undoable) | `git switch`, `git switch -c`, `git add`, `git commit`, `git stash`, `git merge`, `git restore`, `git revert`, `git tag -a` (before push), `git fetch` | the assistant inside an agreed plan; commits follow `docs/TOOLKIT.md` §4 (student approves in interactive mode; allowed inside a recorded delegation) |
| **Publication** (visible to others, hard to take back) | `git push`, opening/merging a pull request, `gh release create`, pushing tags, creating Issues/Projects, changing repository settings, branch protection, adding collaborators, changing remotes | **only the owner**, or the assistant when the owner explicitly asks for that exact action. A delegation never covers publication |

When unsure which row a command belongs to, treat it as publication and ask.

## Inputs

- The question or situation (a conflict, "what branch am I on", "how do we work as five", "make a release").
- The real state, read with read-only commands first (see Actions 1).
- `docs/TOOLKIT.md` §4 (who approves commits), the app's docs folder (from `app-creator.config.json`, `app.docsDir`)
  for `plan.md` slices that map to branches and Issues.
- For teams: who the members are by role (never by email or personal data), and the agreed shared contracts.

## Actions

1. **Look before acting.** Run and read:
   ```bash
   git status
   git branch -vv
   git log --oneline --graph --decorate -15
   git remote -v
   git stash list
   ```
   Explain in plain words: current branch, uncommitted changes (staged = selected for the next commit;
   unstaged = changed but not selected), ahead/behind the remote, and what is only local.
2. **Pick the workflow** for the request and follow its guide:
   - branches, commits, pull requests, review: [branching-and-prs.md](branching-and-prs.md)
   - conflicts, merge vs rebase, recovery: [conflicts-merge-rebase.md](conflicts-merge-rebase.md)
   - releases, tags, Issues, Projects, branch protection: [releases-issues-projects.md](releases-issues-projects.md)
   - a team of about five: [team-of-five.md](team-of-five.md)
3. **One slice, one branch.** Name it after the slice: `feat/csv-export`, `fix/empty-chart`, `docs/setup-guide`.
   Create it from an up-to-date `main`: `git switch main`, `git pull --ff-only` (publication-free: it only
   downloads), `git switch -c feat/csv-export`.
4. **Commit small and verified.** Run `npm run verify` (or the slice's tests) first. Stage specific files, never
   blindly everything: `git add path/one path/two`, check `git diff --staged`, then
   `git commit -m "feat: export the results table as CSV"`. Prefixes: `feat:`, `fix:`, `test:`, `docs:`,
   `refactor:`, `chore:`. Never stage `.env`, `.venv/`, `node_modules/`, caches or screenshots.
5. **Publish only with the owner.** Prepare the push and pull request text; the owner runs `git push -u origin
   <branch>` and opens the PR (or explicitly asks you to).
6. **Switch versions safely** (another branch, a tag such as `m1`, a teammate's branch):
   1. stop running services (`Ctrl+C` in the `npm run dev` / `npm run demo` terminal);
   2. `git status`: if anything is changed, commit it on a branch or `git stash push -m "wip: <what>"`;
   3. `git fetch origin --tags` then `git switch <branch>` or, for a tag, `git switch --detach <tag>`
      (detached = looking at a fixed version; to change it, `git switch -c exercise/<name>` first);
   4. rerun `npm ci` and `npm run setup`, because dependencies may differ between versions;
   5. `npm run demo` or `npm run dev`. Later, get stashed work back with `git stash list` and `git stash pop`.
7. **Recover without destroying anything** (details in [conflicts-merge-rebase.md](conflicts-merge-rebase.md#recovery-without-destructive-commands)):
   save the current state on a rescue branch first (`git switch -c rescue/<date>`), then use `git restore`,
   `git restore --staged`, `git revert <sha>`, `git merge --abort` or `git rebase --abort`.
8. **Report** what changed locally, what still needs the owner (push, PR, release, settings), and the exact commands.

## Outputs

- A plain-language explanation of the state and the proposed commands, each with what it does and how to undo it.
- Local changes only when they are inside the agreed plan (branch, commit, stash, merge, local tag).
- For publication: ready-to-use text (PR description, release notes, suggested branch-protection settings) and the
  exact commands for the owner.

## Verification

- `git status` is clean or shows exactly the intended changes; `git log --oneline -5` shows the expected commits.
- No secret or generated folder was staged: `git diff --staged --name-only` reviewed before every commit.
- After a merge or conflict resolution, `npm run verify` passes before the commit is proposed.
- After switching versions, `npm run setup` ran and the app starts.

## Stop when

- The request is answered and the state is clean, or the next action belongs to the owner (push, PR, release,
  settings). Say so and hand over the exact commands.
- **Stop and ask** when: a command would publish, delete a branch or tag, rewrite history that was pushed,
  or discard uncommitted work; a conflict involves logic you do not understand (ask the author of the other side);
  `git status` shows a state you cannot explain; a secret appears in a commit (tell the owner to revoke the key
  first: deleting it from history does not make it secret again).

## Common mistakes

- Working directly on `main`, so nothing can be reviewed or undone cleanly.
- `git add .` or `git add -A` without looking, committing `.env`, `node_modules/` or screenshots.
- One giant commit "update" mixing three features; reviewers cannot follow it and `git revert` cannot undo one part.
- Switching branches with services running or uncommitted work, then "losing" changes or seeing stale builds.
- Rebasing or force-pushing a branch teammates already pulled.
- Reaching for `git reset --hard` or `git clean -fd` to "make it work": they delete work with no undo.
- Moving a tag that others already fetched.

## Example

Student: "I changed the chart and now I need to look at the `m1` version, but I don't want to lose my work."

```bash
# 1. stop npm run dev with Ctrl+C, then look
git status                                  # shows: modified: app/frontend/src/components/Chart.tsx
git switch -c wip/chart-colours             # keep the work on its own branch
git add app/frontend/src/components/Chart.tsx
git commit -m "wip: try new chart colours"  # local only; nothing is published
git fetch origin --tags
git switch --detach m1                      # look at the fixed m1 version
npm ci && npm run setup && npm run demo
# later: come back
git switch wip/chart-colours && npm ci && npm run setup
```
Report: "Your change is safe on the local branch `wip/chart-colours` (not pushed). You are now viewing `m1`."
