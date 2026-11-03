# Releases, tags, Issues, Projects and branch protection

Part of [git-collaboration](SKILL.md). Creating a tag locally is a local action. Pushing it, creating a GitHub
Release, Issues, Projects or changing settings is **publication (owner)**.

## Tags and releases

A tag is a permanent name for one commit, such as `v1.0` or `m1`. Use **annotated** tags (they record who, when
and why):

```bash
git switch main && git pull --ff-only
npm ci && npm run setup && npm run verify            # tag only verified commits
git tag -a v1.0 -m "v1.0: first classroom release (CSV export, offline demo)"
git show v1.0 --stat                                 # check what it points at
git push origin v1.0                                 # (owner) publish the tag
gh release create v1.0 --title "v1.0" --notes-file docs/CHANGELOG.md   # (owner) optional GitHub Release
```

Rules:

- **Never move or delete a published tag.** People and checkouts rely on it. If the tagged version has a defect,
  fix it in a new commit and tag a new version (`v1.0.1`), and write the defect in the changelog.
- Check whether a tag exists before creating it: `git tag --list 'v1.*'` and `git ls-remote --tags origin`.
- Release notes list what was actually added, how it was verified, and known limitations (see the `write-docs`
  skill). No invented features.
- Students inspect a tag with `git switch --detach v1.0`; to change it they branch first:
  `git switch -c exercise/from-v1 v1.0`.

## Issues

An Issue is a tracked piece of work or bug. One Issue per slice or bug, small enough for one PR.

Template:

```markdown
**Goal:** users can download the results table as CSV.
**Acceptance:** criteria A4.1–A4.3 in docs/acceptance.md.
**Out of scope:** Excel export.
**Owner:** frontend (role) · **Size:** S
```

Bug template: steps to reproduce, expected, actual, version (`git rev-parse --short HEAD`), screenshot. Never paste
keys, `.env` contents or personal data.

```bash
gh issue list                              # read-only
gh issue create --title "..." --body-file issue.md   # (owner)
```

Link PRs to Issues with `Closes #12` in the PR description; the Issue closes when the PR merges.

## Projects (board)

A GitHub Project is a board of Issues and PRs. A simple board for five people:

| Column | Means |
|---|---|
| Backlog | agreed in `plan.md`, not started |
| Ready | contract known, can start today |
| In progress | has an owner and a branch (limit: one per person) |
| In review | PR open, reviewer assigned |
| Done | merged and `npm run verify` green on `main` |

Created by the owner on GitHub. Keep `plan.md` as the source of truth; the board mirrors it.

## Branch protection (suggest, never apply automatically)

Suggested settings for `main`, to be applied **by the owner** in the repository's Settings → Branches (or rulesets):

- [ ] Require a pull request before merging; at least **1 approval**.
- [ ] Dismiss stale approvals when new commits are pushed.
- [ ] Require status checks to pass (the CI job running `npm run verify`, if CI exists; see `prepare-deploy`).
- [ ] Require conversation resolution before merging.
- [ ] Block force pushes and deletion of `main`.
- [ ] Optionally protect release tags (`v*`, `m*`) from deletion and update via a tag ruleset.

The assistant writes this list; it never changes repository settings, collaborators or rulesets itself.
