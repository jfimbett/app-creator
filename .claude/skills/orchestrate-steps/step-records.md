# Step records: templates, dispatcher flags, audit, checkpoints

Part of [orchestrate-steps](SKILL.md). Records are **append-only**: add new files and lines, never rewrite old ones.

## Folder layout

```text
runs/
  INDEX.md                          one line per dispatch, appended by the dispatcher
  <milestone-or-bootstrap>/
    <step-id>/
      PROMPT.md                     written by the owner BEFORE dispatch
      RESPONSE.md                   written by the dispatcher (or by hand: manual capture)
      RESULT.json                   written by the dispatcher
      stderr.log                    only if the CLI wrote to stderr (redacted, last 20 000 characters)
milestones/<nn-name>/
  PROMPT.md                         the milestone's transition brief
  FOLLOWUPS.md                      exact follow-up texts, appended before each is sent
```

## PROMPT.md

```markdown
# PROMPT — m2-03-results-table

- Sender: owner (top-level Claude Code session)
- Receiver: frontend-engineer
- Follow-up of: none            <!-- or the earlier step id and why -->
- Starting commit: 1a2b3c4 (working tree clean)
- Skills to load: build-feature, design-interface, test-and-check
- Key instruction/reference files (sha256 prefix at dispatch):
  - milestones/02-<name>/PROMPT.md 9f0e1d2c3b4a5968
  - .claude/skills/design-interface/SKILL.md 0a1b2c3d4e5f6071
- Dispatch: `node scripts/dispatch-step.mjs --step runs/m2/m2-03-results-table --agent frontend-engineer --milestone m2`

<!-- DISPATCH:BEGIN -->
Task m2-03: results table on the /results page.
Read first: <files>. Contract: <types/endpoint>. Out of scope: <items>.
Done when: criteria A3.1–A3.4 pass; `npm run verify` exits 0; screenshots at 1366 and 390 px looked at.
Do not commit, push or tag. Never read or print .env files.
End with:
## Handoff
Changes: ...
Verification evidence: ...
Remaining findings: ...
Next action: ...
<!-- DISPATCH:END -->
```

Rules: the markers must be on their own lines, exactly as shown (the dispatcher refuses otherwise). Only the text
between them is sent; everything else is metadata. Write the text you will really send: do not replace it later
with a cleaner version.

Hashes and commit:

```bash
git rev-parse --short HEAD
shasum -a 256 milestones/02-<name>/PROMPT.md | cut -c1-16      # Linux: sha256sum; Windows: certutil -hashfile <file> SHA256
```

## Dispatcher flags

`node scripts/dispatch-step.mjs` resolves `--step` against the repository root, so it works from any folder; the
index it appends to is `INDEX.md` two levels above the step (`runs/INDEX.md` for `runs/<milestone>/<step-id>`).
Every flag takes a value; there are no on/off flags and no `--help` (running it without `--step`/`--agent` prints
the usage line and exits 2). An unknown flag, a flag without a value, a `--timeout-min` that is not a number above
0, or an `--agent`/`--mode`/`--resume`/`--model` value with spaces or shell characters also exits 2.

| Flag | Required | Default | Effect |
|---|---|---|---|
| `--step runs/<milestone>/<step-id>` | yes | — | the step folder; must contain PROMPT.md and must not contain RESPONSE.md |
| `--agent <name>` | yes | — | passed as `claude --agent <name>`; the value `default` runs the CLI's default agent (no `--agent`) |
| `--mode <mode>` | no | `acceptEdits` | passed as `--permission-mode`; documented values `acceptEdits`, `bypassPermissions`, `default`, `plan` |
| `--resume <session-id>` | no | none | passed as `--resume`, continuing an earlier session (id from that step's RESULT.json) |
| `--model <id>` | no | CLI default | passed as `--model` |
| `--milestone <name>` | no | name of the step's parent folder | recorded in RESULT.json and INDEX.md |
| `--role-from <sender>` | no | `owner (top-level Claude Code session)` | recorded as the sender |
| `--timeout-min <minutes>` | no | `120` | after this many minutes stops the child and everything it started (POSIX: its process group, SIGTERM then SIGKILL after 10 s; Windows: `taskkill /T /F`); Ctrl+C does the same; the step is recorded as `failed` |

Refusals (exit 2, nothing dispatched), observed on 2026-11-03:

```text
$ node scripts/dispatch-step.mjs
Usage: node scripts/dispatch-step.mjs --step runs/<milestone>/<step-id> --agent <name> [options]
$ node scripts/dispatch-step.mjs --step runs/bootstrap/__nonexistent --agent default
Refusing to dispatch: runs/bootstrap/__nonexistent/PROMPT.md must be written before dispatch.
$ node scripts/dispatch-step.mjs --step runs/bootstrap/B07c-skills-process --agent default
Refusing to overwrite runs/bootstrap/B07c-skills-process/RESPONSE.md (records are append-only). Use a new step id.
```
A PROMPT.md without the DISPATCH block is also refused with exit 2 (from the code; not run). So is a DISPATCH text
that contains something that looks like a credential (any credential pattern below; the message names only the
kind and count, never the value); nothing is sent or recorded, so refer to settings by name instead. If `claude`
cannot be started (not installed or not on PATH), the step is recorded as `failed` with a `failureReason`
(checked on 2026-11-03 against a temporary step folder under `.cache/`).

What it writes:

- `RESULT.json` first with `"status": "dispatched"`, then replaced on completion with: `stepId`, `milestone`,
  `sender`, `receiver`, `dispatcher`, `permissionMode`, `resumeOf`, `model`, `startedAt`, `finishedAt`,
  `startCommit`, `endCommit`, `promptSha256` (of the DISPATCH text), `promptFileSha256`, `status`
  (`completed`/`failed`), `exitCode`, `sessionId`, `numTurns`, `durationMs`, `totalCostUsd`, `modelsUsed`,
  `workingTreeChanged` (count of changed paths), `responseSha256` (of the final message before redaction),
  `missingRecord`. Records written since B16 also have `signal`, `failureReason` (timeout, interruption or start
  failure, else `null`), `responseRedactedSha256` (of the text between the VERBATIM markers, so RESPONSE.md can be
  checked against it), `redactions` and `stderrRedactions` (`{ "<kind>": count }`). Older records without these
  fields stay valid.
  A RESULT.json still saying `dispatched` means the run never finished (crash or still running).
- `RESPONSE.md`: a header (from/to, capture method, session id, finish time, exit code, redaction note), then the
  final message between `<!-- VERBATIM:BEGIN -->` and `<!-- VERBATIM:END -->`. If there was no parseable result:
  `[MISSING FINAL MESSAGE] ... See stderr.log.`
- Redaction markers it inserts (in RESPONSE.md and stderr.log). Credentials: `[REDACTED:openrouter-key]`,
  `[REDACTED:anthropic-key]`, `[REDACTED:api-key]` (`sk-…`, `sk-proj-…`), `[REDACTED:github-token]` (`gh?_…`,
  `github_pat_…`), `[REDACTED:aws-key]`, `[REDACTED:google-key]`, `[REDACTED:slack-token]`, `[REDACTED:private-key]`
  (PEM blocks), `[REDACTED:bearer-token]`, `[REDACTED:secret-value]` (`…API_KEY=`, `…SECRET=`, `…TOKEN=`,
  `…PASSWORD=` with a real-looking value; placeholders are kept). Personal data: `[REDACTED:email]` (addresses at
  `example.com`/`example.org`/`anthropic.com` are kept) and `[REDACTED:user]` for the user name in a home folder
  (`/Users/<name>`, `/home/<name>`, `C:\Users\<name>`).
- `runs/INDEX.md`: one appended line with time, step, agent, status and links (also for failed attempts).

Note: in `claude -p` runs, tool calls that need approval are denied unless the permission mode or the project's
`.claude/settings.json` allows them. A step that "did nothing" may have been blocked; read its RESPONSE.md.

## FOLLOWUPS.md (milestones)

Append before sending; never edit earlier entries.

```markdown
## F3 — 2026-11-03 14:05 — step m2-03b-results-empty-state (follow-up of m2-03-results-table)
Reason: orchestrator judged "repair": empty state missing (criterion A3.4).
Exact text sent:
<!-- FOLLOWUP:BEGIN -->
The results table shows a blank area when there are no rows. Add the empty state ...
<!-- FOLLOWUP:END -->
```

Tool-driven repairs the owner makes by hand (no agent) are logged here too, as "owner repair", with the commands run.

## Audit

Read-only. Save as a temporary file (for example `/tmp/audit-runs.mjs`) and run `node /tmp/audit-runs.mjs` from
the repository root. It prints one line per step and exits 1 if a step needs attention.

```js
import { createHash } from 'node:crypto';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
let problems = 0;
for (const group of readdirSync('runs', { withFileTypes: true }).filter((d) => d.isDirectory())) {
  for (const step of readdirSync(path.join('runs', group.name), { withFileTypes: true }).filter((d) => d.isDirectory())) {
    const dir = path.join('runs', group.name, step.name);
    const has = (f) => existsSync(path.join(dir, f));
    const notes = [];
    if (!has('PROMPT.md')) notes.push('NO PROMPT.md');
    if (!has('RESPONSE.md')) notes.push('NO RESPONSE.md (still running, or a gap to mark)');
    else if (readFileSync(path.join(dir, 'RESPONSE.md'), 'utf8').includes('[MISSING FINAL MESSAGE]')) notes.push('final message missing (marked)');
    if (has('PROMPT.md') && has('RESULT.json')) {
      const block = readFileSync(path.join(dir, 'PROMPT.md'), 'utf8').match(/<!-- DISPATCH:BEGIN -->\r?\n([\s\S]*?)\r?\n<!-- DISPATCH:END -->/);
      const rec = JSON.parse(readFileSync(path.join(dir, 'RESULT.json'), 'utf8'));
      if (!block) notes.push('PROMPT.md has no DISPATCH block');
      else if (rec.promptSha256 && rec.promptSha256 !== createHash('sha256').update(block[1]).digest('hex')) notes.push('PROMPT.md changed after dispatch');
      notes.push(`status ${rec.status}`);
    }
    if (notes.some((n) => /^NO |no DISPATCH|changed|missing/.test(n))) problems++;
    console.log(`${dir}: ${notes.join('; ') || 'ok'}`);
  }
}
console.log(`${problems} step(s) need attention`);
process.exitCode = problems ? 1 : 0;
```

How to act on its output:

| Output | Meaning | Action |
|---|---|---|
| `status completed` | captured | none |
| `NO RESPONSE.md` + `status dispatched` | still running, or the run crashed | wait; if it crashed, write RESPONSE.md containing only a header and `[MISSING FINAL MESSAGE] <reason>`, and dispatch a retry as a new step id |
| `final message missing (marked)` | gap already recorded | make sure the retry or the reason is in INDEX.md/PROGRESS.md |
| `PROMPT.md changed after dispatch` | the record was edited | restore the original from git (`git log -p -- <file>`) or add a note explaining the change; never hide it |
| `NO PROMPT.md` | dispatched without a saved prompt | record the gap honestly; do not write a reconstructed prompt as if it were the original |

## Checkpoints

After the gate passes (owner only):

```bash
git status                                     # clean
npm run verify                                 # exit 0, on this exact commit
git tag --list m2                              # must print nothing: never move an existing tag
git branch milestone/02-<name>                 # local branch at this commit
git tag -a m2 -m "m2: <milestone name>, verified <date>"
git push origin milestone/02-<name> m2         # publication: only with the owner's explicit go-ahead
```

Each milestone starts from the previous tag (`git switch -c milestone/03-<name> m2`), so history stays
cumulative. If an old checkpoint has a defect, fix it with a documented repair commit and a new tag; do not move
the old tag. Record the result SHAs in a final manifest after the checkpoint commits (not inside them).
