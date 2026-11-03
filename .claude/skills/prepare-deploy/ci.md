# Continuous integration with GitHub Actions

Companion to [SKILL.md](SKILL.md). **CI** (continuous integration) means a server runs the project's checks on
every push and pull request, so a broken change is visible before it is merged. Here CI runs exactly what a person
runs: `npm ci && npm run setup && npm run verify`.

Status of the files below: the YAML was parsed locally; they have **not been run on GitHub** from this guide. The
action versions (`@v5`, `@v4`) are the majors current when this was written: check each action's page (for
example github.com/actions/checkout) and update them before use.

## Rules

- **Offline and secret-free.** The checks use the config's `demoEnv` (fixture mode): no API keys, no live
  provider calls, no `.env`. The runner only uses the network to install pinned dependencies. If a check needs a
  secret, the check is wrong, not the workflow.
- **Same commands as locally.** No CI-only test scripts; if CI fails, `npm run verify` on a laptop shows the same
  failure.
- **Least privilege:** `permissions: contents: read`. No deployment, no publishing, no tokens with write access.
- **Actions pinned to full commit SHAs** with the release as a comment (`uses: actions/checkout@<40-hex sha> # v5.1.0`), looked up with `gh api repos/<owner>/<repo>/git/ref/tags/<tag>` (for `"type": "tag"`, dereference with `gh api repos/<owner>/<repo>/git/tags/<sha>`); the `@v5` examples below are shorthand.
- **Pinned toolchain:** Node 22 (the scaffold's `engines` field asks for 22.12 or newer) and a Python between
  3.10 and 3.13 passed to setup through `APP_PYTHON`.

## `.github/workflows/verify.yml`

```yaml
name: verify

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

concurrency:                      # a newer push to the same branch cancels the older run
  group: verify-${{ github.ref }}
  cancel-in-progress: true

jobs:
  verify:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v5

      - uses: actions/setup-node@v5
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: "**/package-lock.json"

      - id: py
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: "**/requirements.lock"

      - name: Cache the project-local Playwright browser
        uses: actions/cache@v4
        with:
          path: .cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}

      - run: npm ci
      - run: npm run setup
        env:
          APP_PYTHON: ${{ steps.py.outputs.python-path }}
      - run: npm run verify

      - name: Keep screenshots and traces for a person to look at
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-results
          path: "**/test-results/"
          if-no-files-found: ignore
          retention-days: 7
```

Notes:

- `npm run setup` skips steps whose lockfile hash is unchanged; the Playwright cache stores its stamp with the
  browser, so a cache hit skips the browser download.
- If Chromium fails to start with "missing libraries" on the runner, add a step before `npm run verify` in the
  frontend folder: `npx playwright install-deps chromium` (it uses `sudo apt-get`; allowed on GitHub-hosted
  runners).
- The screenshots uploaded as an artifact are still evidence for **visual inspection**: someone has to open them.
  A green run is a browser check, not a look.
- With no app configured (the template), `npm run verify` checks the toolkit and the scaffold; the same workflow
  works.

## Optional: check several branches (matrix over refs)

Useful for a maintainer who keeps a `template` branch and `main` (with the example app) and wants both checked
every week or on demand:

```yaml
name: verify-branches

on:
  workflow_dispatch:
  schedule:
    - cron: "0 6 * * 1"          # Mondays 06:00 UTC

permissions:
  contents: read

jobs:
  verify:
    strategy:
      fail-fast: false            # one broken branch does not hide the others
      matrix:
        ref: [main, template]
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v5
        with:
          ref: ${{ matrix.ref }}
      - uses: actions/setup-node@v5
        with:
          node-version: 22
      - id: py
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: npm ci
      - run: npm run setup
        env:
          APP_PYTHON: ${{ steps.py.outputs.python-path }}
      - run: npm run verify
```

A matrix over operating systems (`runs-on: ${{ matrix.os }}` with `ubuntu-latest`, `windows-latest`,
`macos-latest`) checks that the launchers are portable; it costs more runner minutes, so use it for releases, not
every push.

## Checking the workflow before the owner pushes

1. Parse the YAML (any YAML parser, for example `ruby -ryaml -e 'YAML.load_file(ARGV[0])' .github/workflows/verify.yml`).
2. Run the same commands locally in a fresh copy: `npm ci && npm run setup && npm run verify` (exit codes in the
   report).
3. Tell the owner: "the workflow runs after you push; please share the result". Report CI as **not verified**
   until then.

## When CI fails but the laptop passes

| Cause | Fix |
|---|---|
| A file exists locally but is not committed (`git status` shows it untracked or ignored) | commit it, or stop depending on it |
| A test depends on the laptop's `.env`, time zone, or locale | pass settings inline in the test; use UTC and fixed dates |
| Different Python or Node version | match the versions above, or widen the code's compatibility |
| A test reaches the network | mock it (`respx`, `page.route`) |
| Port or timing assumptions | use the ports the launcher chooses; wait for elements, not fixed sleeps |

## Branch protection (owner's decision)

Requiring the `verify` check before merging (Settings → Branches on GitHub) is a repository setting the owner
changes; see `git-collaboration`. Do not change remote settings yourself.
