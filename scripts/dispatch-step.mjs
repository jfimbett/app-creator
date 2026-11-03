#!/usr/bin/env node
// Dispatch one recorded AI step to a Claude Code agent and capture its final message verbatim.
//
//   node scripts/dispatch-step.mjs --step runs/<milestone>/<step-id> --agent <agent-name> \
//        [--mode acceptEdits|bypassPermissions|default|plan] [--resume <session-id>] [--model <id>] \
//        [--milestone <name>] [--role-from <sender>] [--timeout-min 90]
//
// Contract (see .claude/skills/orchestrate-steps/SKILL.md):
//   * <step>/PROMPT.md must already exist (saved BEFORE dispatch). The exact text sent is the part between
//     the markers <!-- DISPATCH:BEGIN --> and <!-- DISPATCH:END -->; everything else is metadata.
//   * The agent's final message (the `result` field of `claude -p --output-format json`) is written to
//     <step>/RESPONSE.md unchanged except for explicit redaction markers ([REDACTED:<kind>]).
//   * <step>/RESULT.json records timestamps, role, status, commits, exit code, session id and cost.
//   * runs/INDEX.md gets one appended line per dispatch (append-only).
// Uses only Node built-ins. Never prints or stores environment variables.
import { spawn, execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { appendFileSync, existsSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) throw new Error(`Unexpected argument: ${a}`);
    out[a.slice(2)] = argv[i + 1];
    i++;
  }
  return out;
}

function git(args) {
  try { return execFileSync('git', args, { encoding: 'utf8' }).trim(); } catch { return null; }
}

// Redact credentials and personal data with explicit markers. Patterns are deliberately broad.
export function redact(text) {
  return text
    .replace(/sk-or-v1-[A-Za-z0-9]{16,}/g, '[REDACTED:openrouter-key]')
    .replace(/sk-ant-[A-Za-z0-9_-]{16,}/g, '[REDACTED:anthropic-key]')
    .replace(/\bgh[pousr]_[A-Za-z0-9]{20,}/g, '[REDACTED:github-token]')
    .replace(/(Bearer\s+)[A-Za-z0-9._-]{16,}/gi, '$1[REDACTED:bearer-token]')
    .replace(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g, (m) =>
      /@(example\.(com|org)|anthropic\.com)$/i.test(m) ? m : '[REDACTED:email]');
}

const args = parseArgs(process.argv.slice(2));
const stepDir = args.step;
const agent = args.agent;
if (!stepDir || !agent) {
  console.error('Usage: node scripts/dispatch-step.mjs --step runs/<milestone>/<step-id> --agent <name> [options]');
  process.exit(2);
}
const promptPath = path.join(stepDir, 'PROMPT.md');
if (!existsSync(promptPath)) {
  console.error(`Refusing to dispatch: ${promptPath} must be written before dispatch.`);
  process.exit(2);
}
if (existsSync(path.join(stepDir, 'RESPONSE.md'))) {
  console.error(`Refusing to overwrite ${stepDir}/RESPONSE.md (records are append-only). Use a new step id.`);
  process.exit(2);
}
const promptFile = readFileSync(promptPath, 'utf8');
const m = promptFile.match(/<!-- DISPATCH:BEGIN -->\r?\n([\s\S]*?)\r?\n<!-- DISPATCH:END -->/);
if (!m) {
  console.error('PROMPT.md has no <!-- DISPATCH:BEGIN --> ... <!-- DISPATCH:END --> block.');
  process.exit(2);
}
const dispatched = m[1];
const sha256 = (s) => createHash('sha256').update(s).digest('hex');
const mode = args.mode || 'acceptEdits';
const milestone = args.milestone || path.basename(path.dirname(stepDir));
const stepId = path.basename(stepDir);
const startedAt = new Date().toISOString();
const startCommit = git(['rev-parse', 'HEAD']);
const resultPath = path.join(stepDir, 'RESULT.json');
const base = {
  stepId, milestone, sender: args['role-from'] || 'owner (top-level Claude Code session)', receiver: agent,
  dispatcher: 'scripts/dispatch-step.mjs (claude -p --output-format json)', permissionMode: mode,
  resumeOf: args.resume || null, model: args.model || 'CLI default', startedAt, startCommit,
  promptSha256: sha256(dispatched), promptFileSha256: sha256(promptFile),
};
writeFileSync(resultPath, JSON.stringify({ ...base, status: 'dispatched' }, null, 2) + '\n');

// --agent default = the CLI's default main agent (used before a dedicated project agent exists).
const cliArgs = ['-p', ...(agent === 'default' ? [] : ['--agent', agent]), '--output-format', 'json', '--permission-mode', mode];
if (args.resume) cliArgs.push('--resume', args.resume);
if (args.model) cliArgs.push('--model', args.model);
const timeoutMs = Number(args['timeout-min'] || 120) * 60_000;

const child = spawn('claude', cliArgs, { stdio: ['pipe', 'pipe', 'pipe'], shell: process.platform === 'win32' });
let stdout = '';
let stderr = '';
child.stdout.on('data', (d) => { stdout += d; });
child.stderr.on('data', (d) => { stderr += d; });
child.stdin.end(dispatched);
const timer = setTimeout(() => { stderr += '\n[dispatch-step] timeout, terminating child\n'; child.kill('SIGTERM'); }, timeoutMs);

child.on('close', (code) => {
  clearTimeout(timer);
  const finishedAt = new Date().toISOString();
  let parsed = null;
  try { parsed = JSON.parse(stdout); } catch { /* handled below */ }
  const result = parsed && typeof parsed.result === 'string' ? parsed.result : null;
  const status = code === 0 && result !== null && !parsed.is_error ? 'completed' : 'failed';
  if (stderr.trim()) writeFileSync(path.join(stepDir, 'stderr.log'), redact(stderr).slice(-20_000));
  const header = [
    `# RESPONSE — ${stepId}`,
    '',
    `- From: ${agent} → to: ${base.sender}`,
    `- Captured by: scripts/dispatch-step.mjs from the \`result\` field of \`claude -p --output-format json\``,
    `- Session id: ${parsed?.session_id ?? 'unknown'} (local Claude Code transcript; not committed)`,
    `- Finished: ${finishedAt}; exit code ${code}; status ${status}`,
    `- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.`,
    '',
    '<!-- VERBATIM:BEGIN -->',
  ].join('\n');
  const body = result !== null ? redact(result)
    : `[MISSING FINAL MESSAGE] The child process produced no parseable result (exit ${code}). See stderr.log.`;
  writeFileSync(path.join(stepDir, 'RESPONSE.md'), `${header}\n${body}\n<!-- VERBATIM:END -->\n`);
  const record = {
    ...base, status, finishedAt, exitCode: code,
    sessionId: parsed?.session_id ?? null, numTurns: parsed?.num_turns ?? null,
    durationMs: parsed?.duration_ms ?? null, totalCostUsd: parsed?.total_cost_usd ?? null,
    modelsUsed: parsed?.modelUsage ? Object.keys(parsed.modelUsage) : null,
    endCommit: git(['rev-parse', 'HEAD']),
    workingTreeChanged: (git(['status', '--porcelain']) || '').split('\n').filter(Boolean).length,
    responseSha256: result !== null ? sha256(result) : null,
    missingRecord: result === null ? 'final message missing' : null,
  };
  writeFileSync(resultPath, JSON.stringify(record, null, 2) + '\n');
  const indexPath = path.join('runs', 'INDEX.md');
  if (!existsSync(indexPath)) writeFileSync(indexPath, '# Step record index\n\nAppend-only. One line per dispatched step.\n\n');
  appendFileSync(indexPath, `- ${finishedAt.slice(0, 16)}Z · **${milestone}/${stepId}** · ${agent} · ${status} · [prompt](${path.relative('runs', promptPath)}) · [response](${path.relative('runs', path.join(stepDir, 'RESPONSE.md'))}) · [result](${path.relative('runs', resultPath)})\n`);
  console.log(`[dispatch-step] ${stepId}: ${status} (exit ${code}), session ${record.sessionId}`);
  process.exit(status === 'completed' ? 0 : 1);
});
