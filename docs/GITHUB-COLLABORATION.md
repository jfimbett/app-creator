# Working together on GitHub (team of five)

For students building an App Creator app as a team. After reading this, your team can split the work, share
code through pull requests, resolve conflicts and release versions without losing anyone's work.

The detailed, command-by-command guides are in the `git-collaboration` skill:
[branches and pull requests](../.claude/skills/git-collaboration/branching-and-prs.md) ·
[conflicts, merge vs rebase, recovery](../.claude/skills/git-collaboration/conflicts-merge-rebase.md) ·
[releases, Issues, Projects, protection](../.claude/skills/git-collaboration/releases-issues-projects.md) ·
[team of five](../.claude/skills/git-collaboration/team-of-five.md).
Ask your AI assistant "use git-collaboration" (Claude Code: `/git-collaboration`) or the `github-coach` agent
when you are unsure what a command will do.

**Nothing here is applied automatically.** The assistant never pushes, opens or merges pull requests, creates
releases, or changes repository settings, branch protection or collaborators. The repository owner does those
things, or explicitly asks the assistant to do one specific action.

## 1. Words you need

| Word | Meaning |
|---|---|
| repository (repo) | the project folder with its full history |
| commit | a saved checkpoint of some files, with a message |
| branch | a separate line of work; `main` is the shared, always-working line |
| clone | your local copy of a repository |
| fork | your own copy of someone else's repository on GitHub |
| `origin` | the GitHub repository your clone came from |
| `upstream` | the original repository you forked from (you add this name yourself) |
| pull request (PR) | a request to merge your branch into `main`, where teammates review it |
| conflict | two branches changed the same lines; a person has to choose |
| tag | a permanent name for one commit, such as `v1.0` |

**Local or published?** Commits, branches, stashes and local tags exist only on your computer until pushed.
`git push`, PRs, releases, Issues and settings are visible to everyone and need the owner.

## 2. Set up once

Shared team repository (everyone added as a collaborator by the owner):

```bash
git clone <repository URL>
cd <repository folder>
npm ci
npm run setup
npm run demo          # open the address it prints; stop with Ctrl+C
```

Fork workflow (you cannot push to the original, for example a course template):

```bash
git clone <URL of your fork>
cd <repository folder>
git remote add upstream <URL of the original>
git remote -v         # origin = your fork, upstream = the original
```

Each person creates their own `.env` from `.env.example` (`cp .env.example .env`) and fills in their own values.
Never commit `.env`, never paste keys into chats, Issues or PRs.

## 3. Roles

Everyone writes code; each role owns the decisions in one area and reviews PRs touching it.

| Role | Owns |
|---|---|
| Product & integration lead | the plan and acceptance criteria, the Issue board, merging to `main`, releases |
| Backend | API endpoints, data, external services, backend tests |
| Frontend | screens, components, wiring to the API |
| Design & accessibility | look and feel, narrow (390 px) and desktop (1366 px) layouts, charts' readability |
| Quality & docs | shared fixtures, browser tests, README and setup docs, review rota |

Rotate roles between milestones if your course wants everyone to try every part. In shared documents, refer to
people by role or GitHub username, not by email or other personal data.

## 4. Shared contracts (agree before working in parallel)

1. **API types**: the JSON each endpoint returns, written once in the architecture document and mirrored in the
   backend model and the frontend types. Missing values are `null`, never `0`.
2. **Fixtures**: one folder of example data everyone uses, labelled recorded or synthetic, with no personal data.
3. **Ownership**: each page and endpoint has one owner; others propose changes by PR.
4. **Commands**: everyone uses `npm run setup`, `npm run dev`, `npm run demo`, `npm run verify`.
5. **Setting names**: in `.env.example` only (names and placeholders).

Change a contract only through a small PR reviewed by everyone who depends on it. Do this first, then build in
parallel.

## 5. The everyday loop

1. Pick an Issue from the board; move it to "In progress".
2. Branch from an up-to-date `main`:
   ```bash
   git switch main
   git pull --ff-only
   git switch -c feat/<short-name>
   ```
3. Work in small steps. Before each commit: `npm run verify`, `git status`, add files by name, read
   `git diff --staged`, then `git commit -m "feat: <what changed>"`.
4. At least once a day, bring in teammates' work: `git fetch origin` then `git merge origin/main`, and run
   `npm run verify` again.
5. Push and open a PR (the owner, or you if the owner made you a collaborator who may push branches):
   `git push -u origin feat/<short-name>`. Describe what, why, how to check, evidence, and what is not done.
   Add `Closes #<issue>`.
6. A teammate reviews: checks out the branch, runs `npm run setup` and `npm run verify`, follows "how to check",
   and comments (blocking or suggestion).
7. After approval and green checks, the integration lead merges (prefer **squash and merge**) and deletes the branch.

Keep PRs small (one topic, under about 400 changed lines) and review within a day.

## 6. Conflicts

When `git merge origin/main` reports a conflict:

1. `git status` lists the files. Open each one and find `<<<<<<<`, `=======`, `>>>>>>>`.
2. Decide what the code should be (often a combination), delete the markers.
3. Lockfiles: do not hand-edit; take one side and regenerate (see the
   [conflicts guide](../.claude/skills/git-collaboration/conflicts-merge-rebase.md)).
4. `npm run verify`, then `git add <files>` and `git commit`.
5. Lost? `git merge --abort` returns you to where you started. Ask the teammate who wrote the other side.

**Merge, don't rebase, shared branches.** Rebasing rewrites commits other people already have. Never force-push
to a shared branch.

## 7. Switching versions safely

To look at a teammate's branch or a released tag:

1. Stop running services (Ctrl+C).
2. `git status`. If you have changes, commit them on your branch or `git stash push -m "wip: <what>"`.
3. `git fetch origin --tags`, then `git switch <branch>` or `git switch --detach <tag>`.
4. `npm ci` and `npm run setup` (dependencies may differ), then `npm run demo`.

Never use `git reset --hard` or `git clean -fd` to "make checkout work": they delete work with no undo. If git is
in a state you do not understand, make a rescue branch (`git switch -c rescue/<date>`) and ask.

## 8. Suggested protections (the owner applies them, if wanted)

For `main`, in the repository's Settings → Branches (or Rules):

- Require a pull request with at least 1 approval; dismiss stale approvals on new commits.
- Require status checks to pass (a CI job running `npm run verify`, if your team adds CI).
- Require conversation resolution before merging.
- Block force pushes and deletion.
- Protect release tags from being moved or deleted.

These are suggestions. Nobody's assistant changes repository settings.

## 9. Releases

At the end of a milestone the integration lead checks `main` in a fresh clone (`npm ci`, `npm run setup`,
`npm run verify`), writes the changelog (what was added, how it was verified, known limitations), and the owner
creates and pushes an **annotated** tag (`git tag -a v1.0 -m "..."`, then `git push origin v1.0`). A published tag
is never moved; a fix gets a new tag (`v1.0.1`).

_Status: written 2026-11-03 for the App Creator template. The git commands are standard git; the root `npm run`
commands follow `docs/TOOLKIT.md` §3. The full team workflow on GitHub has not been rehearsed with a real
five-person team in this repository._
