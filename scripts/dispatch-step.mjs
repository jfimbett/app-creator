#!/usr/bin/env node
// Dispatch one recorded AI step to a Claude Code agent and capture its final message verbatim.
//
//   node scripts/dispatch-step.mjs --step runs/<milestone>/<step-id> --agent <agent-name> \
//        [--mode acceptEdits|bypassPermissions|default|plan] [--resume <session-id>] [--model <id>] \
//        [--milestone <name>] [--role-from <sender>] [--timeout-min 120]
//
// Contract (see .claude/skills/orchestrate-steps/SKILL.md):
//   * <step>/PROMPT.md must already exist (saved BEFORE dispatch). The exact text sent is the part between
//     the markers <!-- DISPATCH:BEGIN --> and <!-- DISPATCH:END -->; everything else is metadata.
//     A DISPATCH text that contains something that looks like a credential is refused (exit 2, nothing sent).
//   * The agent's final message (the `result` field of `claude -p --output-format json`) is written to
//     <step>/RESPONSE.md unchanged except for explicit redaction markers ([REDACTED:<kind>]).
//   * <step>/RESULT.json records timestamps, role, status, commits, exit code, session id, cost, redaction
//     counts, and hashes of the final message before (responseSha256) and after (responseRedactedSha256)
//     redaction; the second one matches the text between the VERBATIM markers of RESPONSE.md.
//   * <records>/INDEX.md (runs/INDEX.md for runs/<milestone>/<step-id>) gets one appended line per dispatch.
//   * --step is resolved against the repository root, so the script works from any folder.
// Uses only Node built-ins. Never prints or stores environment variables or the values it redacts.
import { execFileSync, spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { appendFileSync, existsSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const IS_WIN = process.platform === 'win32';
const USAGE = 'Usage: node scripts/dispatch-step.mjs --step runs/<milestone>/<step-id> --agent <name> [options]';
const FLAGS = ['step', 'agent', 'mode', 'resume', 'model', 'milestone', 'role-from', 'timeout-min'];
const CLI_VALUE = /^[A-Za-z0-9._:@/[\]-]+$/; // values handed to the claude CLI: no spaces or shell characters
const KILL_GRACE_MS = 10_000;
const CLOSE_GRACE_MS = 5_000;

// ---------------------------------------------------------------- redaction

const marker = (kind) => `[REDACTED:${kind}]`;
const hasLetterAndDigit = (v) => /[A-Za-z]/.test(v) && /\d/.test(v);

// Each rule: kind, global regex, optional `to(match, ...groups)` returning the replacement or null (keep).
// Credential rules come first; their presence in a dispatched prompt blocks the dispatch.
const CREDENTIAL_RULES = [
  { kind: 'openrouter-key', re: /sk-or-v1-[A-Za-z0-9]{16,}/g },
  { kind: 'anthropic-key', re: /sk-ant-[A-Za-z0-9_-]{16,}/g },
  { kind: 'api-key', re: /\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}/g },
  { kind: 'github-token', re: /\bgh[pousr]_[A-Za-z0-9]{20,}/g },
  { kind: 'github-token', re: /\bgithub_pat_[A-Za-z0-9_]{20,}/g },
  { kind: 'aws-key', re: /\bAKIA[0-9A-Z]{16}\b/g },
  { kind: 'google-key', re: /\bAIza[0-9A-Za-z_-]{30,}/g },
  { kind: 'slack-token', re: /\bxox[abprs]-[A-Za-z0-9-]{10,}/g },
  { kind: 'private-key', re: /-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----/g },
  { kind: 'bearer-token', re: /(Bearer\s+)[A-Za-z0-9._~+/=-]{16,}/gi, to: (m, lead) => `${lead}${marker('bearer-token')}` },
  {
    // NAME_API_KEY=value, SECRET: value, ...; placeholders (<...>, ${...}, words without digits) are kept.
    kind: 'secret-value',
    re: /\b([A-Z0-9_]*(?:API_KEY|SECRET|SECRET_KEY|TOKEN|PASSWORD|PASSWD))(\s*[:=]\s*)(['"]?)([^\s'"]{12,})\3/g,
    to: (m, name, sep, quote, value) => (/^[<$%{[]/.test(value) || !hasLetterAndDigit(value) ? null
      : `${name}${sep}${quote}${marker('secret-value')}${quote}`),
  },
];

const PERSONAL_RULES = [
  {
    kind: 'email',
    re: /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g,
    to: (m) => (/@(example\.(com|org)|anthropic\.com)$/i.test(m) ? null : marker('email')),
  },
  {
    // A home folder shows the OS user name: /Users/<name>, /home/<name>, C:\Users\<name>.
    kind: 'user',
    re: /(\/Users\/|\/home\/|[Cc]:\\Users\\)[^/\\\s"'`()<>[\]]+/g, // no "[": markers and quoted regexes stay
    to: (m, lead) => `${lead}${marker('user')}`,
  },
];

function applyRules(text, rules, counts) {
  let out = text;
  for (const { kind, re, to } of rules) {
    out = out.replace(re, (...args) => {
      const replacement = to ? to(...args) : marker(kind);
      if (replacement === null) return args[0];
      counts[kind] = (counts[kind] || 0) + 1;
      return replacement;
    });
  }
  return out;
}

/** Redacts credentials and personal data with explicit markers; returns { text, counts: { kind: n } }. */
export function redactWithCounts(text) {
  const counts = {};
  const out = applyRules(applyRules(text, CREDENTIAL_RULES, counts), PERSONAL_RULES, counts);
  return { text: out, counts };
}

/** Redacts credentials and personal data with explicit markers. Patterns are deliberately broad. */
export function redact(text) {
  return redactWithCounts(text).text;
}

/** Counts of credential-like strings in `text` (kinds only; the values are never returned). */
export function credentialCounts(text) {
  const counts = {};
  applyRules(text, CREDENTIAL_RULES, counts);
  return counts;
}

// ---------------------------------------------------------------- helpers

const sha256 = (s) => createHash('sha256').update(s).digest('hex');
const toPosix = (p) => p.split(path.sep).join('/');
const fromRoot = (p) => toPosix(path.relative(REPO_ROOT, p)) || '.';

function refuse(message) {
  console.error(message);
  process.exit(2);
}

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i += 2) {
    const flag = argv[i];
    const name = flag.startsWith('--') ? flag.slice(2) : null;
    if (!name) refuse(`Unexpected argument: ${flag}\n${USAGE}`);
    if (!FLAGS.includes(name)) refuse(`Unknown flag: ${flag}. Known flags: ${FLAGS.map((f) => `--${f}`).join(', ')}.`);
    const value = argv[i + 1];
    if (value === undefined || value.startsWith('--')) refuse(`${flag} needs a value.`);
    out[name] = value;
  }
  return out;
}

function git(args) {
  try {
    return execFileSync('git', args, { cwd: REPO_ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch {
    return null;
  }
}

/** Kills the child and everything it started: its process group (POSIX) or process tree (Windows). */
function killTree(child, signal) {
  if (!child.pid) return;
  try {
    if (IS_WIN) spawnSync('taskkill', ['/PID', String(child.pid), '/T', '/F'], { stdio: 'ignore', windowsHide: true });
    else process.kill(-child.pid, signal);
  } catch { /* already gone */ }
}

function startClaude(cliArgs) {
  if (IS_WIN) {
    // claude is a .cmd shim on Windows, which only runs through a shell. Every argument matched CLI_VALUE (no
    // spaces or shell characters), so quoting each one is enough; one command line avoids Node's DEP0190.
    const line = ['claude', ...cliArgs].map((a) => `"${a}"`).join(' ');
    return spawn(line, { shell: true, stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
  }
  // Own process group, so a timeout or Ctrl+C can stop claude together with the tools it started.
  return spawn('claude', cliArgs, { stdio: ['pipe', 'pipe', 'pipe'], detached: true });
}

// ---------------------------------------------------------------- main

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.step || !args.agent) refuse(USAGE);
  for (const name of ['agent', 'mode', 'resume', 'model']) {
    if (args[name] !== undefined && !CLI_VALUE.test(args[name])) {
      refuse(`--${name} may contain only letters, digits and . _ : @ / [ ] -`);
    }
  }
  const timeoutMin = Number(args['timeout-min'] ?? 120);
  if (!Number.isFinite(timeoutMin) || timeoutMin <= 0) refuse('--timeout-min must be a number of minutes above 0.');

  const stepDir = path.resolve(REPO_ROOT, args.step);
  const recordsRoot = path.dirname(path.dirname(stepDir));
  const rootFromRecords = path.relative(recordsRoot, REPO_ROOT);
  if (!rootFromRecords.startsWith('..') && !path.isAbsolute(rootFromRecords)) { // records root = repo root or above
    refuse(`--step must be <records>/<milestone>/<step-id>, for example runs/m01/s01 (got ${args.step}).`);
  }
  const promptPath = path.join(stepDir, 'PROMPT.md');
  if (!existsSync(promptPath)) refuse(`Refusing to dispatch: ${fromRoot(promptPath)} must be written before dispatch.`);
  if (existsSync(path.join(stepDir, 'RESPONSE.md'))) {
    refuse(`Refusing to overwrite ${fromRoot(stepDir)}/RESPONSE.md (records are append-only). Use a new step id.`);
  }
  const promptFile = readFileSync(promptPath, 'utf8');
  const m = promptFile.match(/<!-- DISPATCH:BEGIN -->\r?\n([\s\S]*?)\r?\n<!-- DISPATCH:END -->/);
  if (!m) refuse('PROMPT.md has no <!-- DISPATCH:BEGIN --> ... <!-- DISPATCH:END --> block.');
  const dispatched = m[1];
  const found = credentialCounts(dispatched);
  if (Object.keys(found).length) {
    const kinds = Object.entries(found).map(([k, n]) => `${k} ×${n}`).join(', ');
    refuse(`Refusing to dispatch: the DISPATCH text of ${fromRoot(promptPath)} contains what looks like a credential ` +
      `(${kinds}). Remove it (refer to the setting by name instead). Nothing was sent or recorded.`);
  }
  dispatch({ args, stepDir, recordsRoot, promptPath, promptFile, dispatched, timeoutMs: timeoutMin * 60_000 });
}

function dispatch({ args, stepDir, recordsRoot, promptPath, promptFile, dispatched, timeoutMs }) {
  const agent = args.agent;
  const mode = args.mode || 'acceptEdits';
  const milestone = args.milestone || path.basename(path.dirname(stepDir));
  const stepId = path.basename(stepDir);
  const resultPath = path.join(stepDir, 'RESULT.json');
  const base = {
    stepId, milestone, sender: args['role-from'] || 'owner (top-level Claude Code session)', receiver: agent,
    dispatcher: 'scripts/dispatch-step.mjs (claude -p --output-format json)', permissionMode: mode,
    resumeOf: args.resume || null, model: args.model || 'CLI default', startedAt: new Date().toISOString(),
    startCommit: git(['rev-parse', 'HEAD']), promptSha256: sha256(dispatched), promptFileSha256: sha256(promptFile),
  };
  writeFileSync(resultPath, JSON.stringify({ ...base, status: 'dispatched' }, null, 2) + '\n');

  // --agent default = the CLI's default main agent (used before a dedicated project agent exists).
  const cliArgs = ['-p', ...(agent === 'default' ? [] : ['--agent', agent]), '--output-format', 'json', '--permission-mode', mode];
  if (args.resume) cliArgs.push('--resume', args.resume);
  if (args.model) cliArgs.push('--model', args.model);

  const child = startClaude(cliArgs);
  let stdout = '';
  let stderr = '';
  let failureReason = null;
  const timers = [];
  const note = (text) => { stderr += `\n[dispatch-step] ${text}\n`; };
  const stop = (reason) => {
    if (failureReason) return;
    failureReason = reason;
    note(`${reason}, terminating child`);
    killTree(child, 'SIGTERM');
    timers.push(setTimeout(() => killTree(child, 'SIGKILL'), KILL_GRACE_MS));
  };

  let finished = false;
  const finish = (code, signal) => {
    if (finished) return;
    finished = true;
    for (const t of timers) clearTimeout(t);
    writeRecords({ base, stepDir, recordsRoot, promptPath, resultPath, agent, stdout, stderr, code, signal, failureReason });
  };

  child.stdout.on('data', (d) => { stdout += d; });
  child.stderr.on('data', (d) => { stderr += d; });
  child.stdin.on('error', () => { /* the child exited before reading its prompt; reported through exit/close */ });
  child.on('error', (err) => {
    if (child.pid) { note(err.message); return; } // e.g. a failed kill; the process is still running
    failureReason = `could not start claude (${err.code || err.message}); is Claude Code installed and on PATH?`;
    note(failureReason);
    finish(null, null);
  });
  // 'close' waits for every pipe; if something the child started still holds one, give up waiting after a grace.
  child.on('exit', (code, signal) => { timers.push(setTimeout(() => finish(code, signal), CLOSE_GRACE_MS)); });
  child.on('close', (code, signal) => finish(code, signal));
  timers.push(setTimeout(() => stop(`timeout after ${timeoutMs / 60_000} min`), timeoutMs));
  for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) process.on(sig, () => stop(`interrupted (${sig})`));
  child.stdin.end(dispatched);
}

function writeRecords({ base, stepDir, recordsRoot, promptPath, resultPath, agent, stdout, stderr, code, signal, failureReason }) {
  const finishedAt = new Date().toISOString();
  let parsed = null;
  try { parsed = JSON.parse(stdout); } catch { /* handled below */ }
  const result = parsed && typeof parsed.result === 'string' ? parsed.result : null;
  const status = code === 0 && result !== null && !parsed.is_error && !failureReason ? 'completed' : 'failed';
  const stderrRedacted = redactWithCounts(stderr);
  if (stderr.trim()) writeFileSync(path.join(stepDir, 'stderr.log'), stderrRedacted.text.slice(-20_000));
  const header = [
    `# RESPONSE — ${base.stepId}`,
    '',
    `- From: ${agent} → to: ${base.sender}`,
    `- Captured by: scripts/dispatch-step.mjs from the \`result\` field of \`claude -p --output-format json\``,
    `- Session id: ${parsed?.session_id ?? 'unknown'} (local Claude Code transcript; not committed)`,
    `- Finished: ${finishedAt}; exit code ${code}; status ${status}`,
    `- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.`,
    '',
    '<!-- VERBATIM:BEGIN -->',
  ].join('\n');
  const redacted = result !== null ? redactWithCounts(result) : null;
  const body = redacted ? redacted.text
    : `[MISSING FINAL MESSAGE] The child process produced no parseable result (exit ${code}). See stderr.log.`;
  writeFileSync(path.join(stepDir, 'RESPONSE.md'), `${header}\n${body}\n<!-- VERBATIM:END -->\n`);
  const record = {
    ...base, status, finishedAt, exitCode: code, signal: signal ?? null, failureReason,
    sessionId: parsed?.session_id ?? null, numTurns: parsed?.num_turns ?? null,
    durationMs: parsed?.duration_ms ?? null, totalCostUsd: parsed?.total_cost_usd ?? null,
    modelsUsed: parsed?.modelUsage ? Object.keys(parsed.modelUsage) : null,
    endCommit: git(['rev-parse', 'HEAD']),
    workingTreeChanged: (git(['status', '--porcelain']) || '').split('\n').filter(Boolean).length,
    responseSha256: result !== null ? sha256(result) : null,
    responseRedactedSha256: redacted ? sha256(redacted.text) : null,
    redactions: redacted ? redacted.counts : {},
    stderrRedactions: stderrRedacted.counts,
    missingRecord: result === null ? 'final message missing' : null,
  };
  writeFileSync(resultPath, JSON.stringify(record, null, 2) + '\n');
  const indexPath = path.join(recordsRoot, 'INDEX.md');
  if (!existsSync(indexPath)) writeFileSync(indexPath, '# Step record index\n\nAppend-only. One line per dispatched step.\n\n');
  const link = (p) => toPosix(path.relative(recordsRoot, p));
  appendFileSync(indexPath, `- ${finishedAt.slice(0, 16)}Z · **${base.milestone}/${base.stepId}** · ${agent} · ${status} · ` +
    `[prompt](${link(promptPath)}) · [response](${link(path.join(stepDir, 'RESPONSE.md'))}) · [result](${link(resultPath)})\n`);
  console.log(`[dispatch-step] ${base.stepId}: ${status} (exit ${code}), session ${record.sessionId}`);
  process.exit(status === 'completed' ? 0 : 1);
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) main();
