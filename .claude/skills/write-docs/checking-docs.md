# Checking docs against reality

Part of [write-docs](SKILL.md). Run these before saying documentation is done.

## 1. Keep a run log while writing

Record each command you document, in the step record or your handoff:

```text
2026-11-03  macOS 15.x  node v22.x  python 3.12.x
$ npm ci                 -> exit 0
$ npm run setup          -> exit 0 (backend .venv created, frontend installed, Chromium installed)
$ npm run verify         -> exit 0
$ npm run demo           -> served http://localhost:3000, stopped with Ctrl+C
NOT RUN: npm run dev in live mode (needs a key the writer must not handle)
```

Versions: `node --version`, `npm --version`, `git --version`, and the Python the setup script reports.

## 2. Commands in docs exist

```bash
# scripts the root package.json really has
node -e "console.log(Object.keys(require('./package.json').scripts).join('\n'))"
# every "npm run X" written in the docs
grep -rhoE 'npm run [a-z:-]+' README.md docs/ | sort -u
```
Every name in the second list must be in the first. Do the same for the app's own `package.json` if the docs
mention commands run inside `<frontendDir>`.

## 3. Links and paths resolve

```bash
npm run check-toolkit     # checks relative links in all *.md files, skill frontmatter, the skills index
```
For paths written in backticks (not links), check them by hand: `ls <path>`.

## 4. Settings match `.env.example`

```bash
# names only: the part before "=" on non-comment lines (never open .env itself)
grep -oE '^[A-Z][A-Z0-9_]*' .env.example | sort -u
```
Every setting the docs mention must be in that list, and every required one must be documented.

## 5. Versions agree

Compare what the docs say with `package.json` → `engines.node`, the Python range the setup script prints, and
`docs/TOOLKIT.md`. If two sources disagree, report it as a finding naming both files; do not pick one silently.

## 6. No secrets or personal data

```bash
grep -nE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}|sk-[A-Za-z0-9_-]{10,}|gh[pousr]_[A-Za-z0-9]{20,}|/Users/[a-z]+/|C:\\\\Users\\\\' <files>
```
Expected: no output (example domains such as `example.com` are fine where a format must be shown).

## 7. Fresh-clone walk-through (best evidence)

```bash
git clone <repository path or URL> /tmp/docs-check && cd /tmp/docs-check
# follow the README literally, copying each command; note every place you had to guess
```
Remove only the temporary folder you created afterwards. If you could not do this, write
"setup steps checked individually, not followed end to end in a fresh clone".
