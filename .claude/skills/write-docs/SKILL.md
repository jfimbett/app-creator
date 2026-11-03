---
name: write-docs
description: Use when writing or updating a README, setup or run instructions, troubleshooting, a changelog, release notes, an architecture diagram or teaching notes, after a change to how the app is installed, run or used, or when someone could not follow the docs.
---

# Write documentation that matches what was actually run

Good docs let a beginner go from a fresh clone to a running app without asking anyone. The rule that makes them
trustworthy: **every command in the docs was run, with its result seen, or it is labelled "not verified".**

## Inputs

- `app-creator.config.json`: the app's `frontendDir`, `backendDir` and `docsDir` (written `<docs>` below). With
  `"app": null` the repository is the template and there is no app to document yet.
- The root contract in `docs/TOOLKIT.md` §3 (`npm ci`, `npm run setup | dev | demo | verify | create-app`) and the
  root `package.json` scripts.
- `<docs>/product.md`, `<docs>/architecture.md`, `<docs>/acceptance.md`, `<docs>/plan.md` (progress and known
  problems), the existing README files.
- `.env.example` (setting **names** only; never open `.env`).
- Recent verification output: from your own runs, or the output quoted in the brief or step record.

## Actions

1. **Name the reader and the job.** One document, one purpose:
   | Document | Reader | After reading they can |
   |---|---|---|
   | `README.md` (root or app) | newcomer | say what the app is, install, run the demo |
   | `docs/SETUP.md` | student on a fresh machine | install, configure, run, test, switch versions, fix common errors |
   | `docs/ARCHITECTURE.md` | teammate, reviewer | find where things live and how data flows |
   | `docs/CHANGELOG.md`, release notes | everyone | see what changed in each version and what does not work |
   | `docs/TEACHING-GUIDE.md` | instructor | rehearse and run a short demo, give exercises |
   | `docs/TROUBLESHOOTING` section | anyone stuck | match an error message to a fix |
   Link instead of repeating; a fact lives in one place.
2. **Collect the real commands** from `package.json`, the launchers' printed guidance, and the app's README.
3. **Run the safe ones** and keep the output: `npm ci`, `npm run setup`, `npm run verify`, `npm run demo`
   (stop with Ctrl+C), `node --version`. Record the exit code and the date. Never run publication commands
   (push, release) to "check" them.
4. **Write** with the templates in [doc-templates.md](doc-templates.md): short sentences, numbered steps, the exact
   command, **what you should see**, and **if it fails**. Define a term the first time ("a virtual environment
   (`.venv`) is a private folder of Python packages for this project").
5. **Label honestly.** Each command block is either verified (`Checked <date> on <OS>, Node <v>, Python <v>`) or
   marked `Not verified:` with the reason (needs a key, needs Windows, needs the network). Results, numbers and
   screenshots in docs come from real runs, never invented.
6. **Settings:** list each name from `.env.example` with what it does and whether it is required; tell the reader
   to `cp .env.example .env` and fill in their own values. Never show a real value; never ask anyone to paste a key
   into a chat.
7. **Known problems** come from `<docs>/plan.md` and the latest verification, copied honestly, with workarounds.
8. **Check the docs against reality** with [checking-docs.md](checking-docs.md): every relative link and path
   exists, every command matches `package.json`, versions match the engines/lockfiles, and `npm run check-toolkit`
   passes. Report any disagreement between docs and code instead of guessing which is right.

## Outputs

- The updated document(s), each with a "last checked" line (date and versions).
- A list of commands run with exit codes, and of steps labelled not verified.
- Findings: docs/code disagreements and code fixes needed (docs writers do not change code).

## Verification

- `npm run check-toolkit` exits 0 (it checks relative links in every `*.md`).
- Each command in the new text appears in your run log or is labelled `Not verified`.
- `grep -rn "TODO\|TBD\|lorem" <the files you changed>` finds nothing unintended.
- No email address, key-like string or `.env` value in the docs:
  `grep -nE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}|sk-[A-Za-z0-9]{10,}' <files>` finds nothing.
- For setup docs: ideally someone follows them in a fresh clone (`git clone <url> /tmp/try && cd /tmp/try`);
  otherwise say they were not followed end to end.

## Stop when

- The documents are written, checked and the findings reported.
- **Stop and ask** when: the docs and the code disagree and you cannot tell which is right; a step can only be
  checked with a secret, money or a publication action; the requested content describes a feature that does not
  exist or is out of the MVP; a command fails twice (report it as a finding with its output, do not document a
  workaround you have not seen work).

## Common mistakes

- Copying commands from memory or another project; they drift from `package.json`.
- "Run the app" without the exact command, URL and what the screen should show.
- Claiming "works on Windows" after testing only macOS.
- Screenshots or numbers from an older version, or made up to look complete.
- Repeating the same setup steps in four files, so three of them go stale.
- Putting real keys, emails or a personal path (`/Users/<name>/...`) in examples.

## Example

Brief: "the demo command changed; update the README."

1. `cat package.json` shows `"demo": "node scripts/demo.mjs"`. Run `npm run setup` (exit 0) and `npm run demo`:
   the terminal prints the frontend URL; `http://localhost:3000` shows the home page with fixture data; Ctrl+C stops it.
2. README section written:
   ````markdown
   ## Try the demo (offline, no keys)
   1. `npm ci` then `npm run setup` (first time: several minutes; it ends with a "next steps" message).
   2. `npm run demo`, then open http://localhost:3000. You should see the home page with example data.
   3. Stop with Ctrl+C.
   **If it fails:** "port 3000 is in use" → close the other app or run `FRONTEND_PORT=3001 npm run demo`.
   _Checked 2026-11-03 on macOS 15, Node 22, Python 3.12._
   ````
3. Finding reported: "`docs/SETUP.md` still says `npm start`; no such script exists."
