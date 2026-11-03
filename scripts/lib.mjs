// Shared helpers for the App Creator root launchers (setup, dev, demo, verify, create-app, check-toolkit).
// Node built-ins only (no npm dependencies), so `npm ci` at the root installs nothing and the scripts run
// on macOS, Linux and Windows. Rules kept here:
//   - never kill a process we did not start (ports in use are refused, not freed);
//   - never print values from the optional root .env file;
//   - long-running children get their own process group so Ctrl+C cleans up the whole tree.

import { spawn, spawnSync, execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const IS_WIN = process.platform === 'win32';
export const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const CONFIG_PATH = path.join(REPO_ROOT, 'app-creator.config.json');
export const CACHE_DIR = path.join(REPO_ROOT, '.cache');
export const BROWSERS_PATH = path.join(CACHE_DIR, 'ms-playwright');
export const NODE_MIN = [22, 13, 0];
export const PYTHON_MIN = [3, 10];
export const PYTHON_MAX = [3, 13];

// ---------------------------------------------------------------- output

const useColor = process.stdout.isTTY && !process.env.NO_COLOR;
const paint = (code) => (s) => (useColor ? `\x1b[${code}m${s}\x1b[0m` : s);
export const c = { bold: paint(1), dim: paint(2), red: paint(31), green: paint(32), yellow: paint(33), cyan: paint(36) };

/** Prints a section heading. */
export function heading(text) {
  console.log(`\n${c.bold(c.cyan(`== ${text}`))}`);
}

/** Stops the script with a readable message (no stack trace). */
export function fail(message, code = 1) {
  console.error(`\n${c.red('Error:')} ${message}`);
  process.exit(code);
}

// ---------------------------------------------------------------- config

export const APP_DEFAULTS = {
  backendApp: 'app.main:app',
  healthPath: '/api/health',
  ports: { backend: 8000, frontend: 3000 },
  devEnv: {},
  demoEnv: {},
  smokeSpec: 'e2e',
};

/**
 * Reads app-creator.config.json. Returns { raw, app } where `app` is null (template mode) or an object with
 * absolute paths (frontendDir, backendDir, docsDir) and every default filled in. Ports honour the
 * BACKEND_PORT / FRONTEND_PORT environment variables (process env or root .env).
 */
export function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) fail(`missing ${CONFIG_PATH}. Restore it from git (git checkout app-creator.config.json).`);
  let raw;
  try {
    raw = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  } catch (err) {
    fail(`app-creator.config.json is not valid JSON: ${err.message}`);
  }
  return { raw, app: raw.app ? resolveApp(raw.app) : null };
}

/** Fills defaults into an app entry and resolves its directories against `base` (the repo root by default). */
export function resolveApp(entry, base = REPO_ROOT) {
  for (const key of ['name', 'frontendDir', 'backendDir']) {
    if (!entry[key]) fail(`app-creator.config.json: "app.${key}" is required when "app" is set.`);
  }
  const env = mergedEnv();
  const app = { ...APP_DEFAULTS, ...entry, ports: { ...APP_DEFAULTS.ports, ...(entry.ports || {}) } };
  app.frontendDir = path.resolve(base, entry.frontendDir);
  app.backendDir = path.resolve(base, entry.backendDir);
  app.docsDir = path.resolve(base, entry.docsDir || 'docs');
  app.ports.backend = portFrom(env.BACKEND_PORT, 'BACKEND_PORT') ?? app.ports.backend;
  app.ports.frontend = portFrom(env.FRONTEND_PORT, 'FRONTEND_PORT') ?? app.ports.frontend;
  return app;
}

function portFrom(value, name) {
  if (value === undefined || value === '') return undefined;
  const n = Number(value);
  if (!Number.isInteger(n) || n < 1024 || n > 65535) fail(`${name} must be a whole number between 1024 and 65535.`);
  return n;
}

export function writeConfig(raw) {
  fs.writeFileSync(CONFIG_PATH, `${JSON.stringify(raw, null, 2)}\n`);
}

/** Paths stored in the config are repo-relative with forward slashes (portable across OSes). */
export function toConfigPath(abs) {
  return path.relative(REPO_ROOT, abs).split(path.sep).join('/');
}

// ---------------------------------------------------------------- environment (.env)

let dotEnvCache;

/**
 * Reads the optional root `.env` (KEY=VALUE lines, # comments, optional quotes, optional `export `).
 * Values are returned to the caller but never printed by these scripts.
 */
export function loadDotEnv() {
  if (dotEnvCache) return dotEnvCache;
  dotEnvCache = {};
  const file = path.join(REPO_ROOT, '.env');
  if (!fs.existsSync(file)) return dotEnvCache;
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const m = line.match(/^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (!m) continue;
    let value = m[2];
    if (/^(['"]).*\1$/.test(value)) value = value.slice(1, -1);
    else value = value.replace(/\s+#.*$/, '');
    dotEnvCache[m[1]] = value;
  }
  return dotEnvCache;
}

/** process.env wins over .env (so `BACKEND_PORT=8001 npm run dev` works), then `extra` wins over both. */
export function mergedEnv(extra = {}) {
  return { ...loadDotEnv(), ...process.env, NEXT_TELEMETRY_DISABLED: '1', ...extra };
}

// ---------------------------------------------------------------- versions

function parseVersion(text) {
  const m = String(text).match(/(\d+)\.(\d+)(?:\.(\d+))?/);
  return m ? [Number(m[1]), Number(m[2]), Number(m[3] || 0)] : null;
}

function cmpVersion(a, b) {
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    const d = (a[i] || 0) - (b[i] || 0);
    if (d) return d;
  }
  return 0;
}

/** Exits with guidance if Node is older than the supported floor. Returns the version string. */
export function checkNode() {
  const v = process.versions.node;
  if (cmpVersion(parseVersion(v), NODE_MIN) < 0) {
    fail(`Node ${v} is too old; App Creator needs Node ${NODE_MIN.join('.')} or newer (22 LTS or 24 LTS).\n` +
      '  Install it from https://nodejs.org (or switch with nvm / fnm), open a new terminal, and run the command again.');
  }
  return v;
}

const PY_PROBE = 'import sys; print("%d.%d.%d" % sys.version_info[:3]); print(sys.executable)';

/** Runs `cmd args -c PY_PROBE`; returns { version, executable } or null. */
export function probePython(cmd, args = []) {
  try {
    const out = execFileSync(cmd, [...args, '-c', PY_PROBE], { encoding: 'utf8', timeout: 15000, stdio: ['ignore', 'pipe', 'ignore'], windowsHide: true });
    const [version, executable] = out.trim().split(/\r?\n/);
    const parsed = parseVersion(version);
    return parsed ? { version, parsed, executable: executable.trim() } : null;
  } catch {
    return null;
  }
}

export function isSupportedPython(parsed) {
  const mm = parsed.slice(0, 2);
  return cmpVersion(mm, PYTHON_MIN) >= 0 && cmpVersion(mm, PYTHON_MAX) <= 0;
}

const SUPPORTED_RANGE = `${PYTHON_MIN.join('.')}–${PYTHON_MAX.join('.')}`;

/**
 * Finds a Python between 3.10 and 3.13. Order: APP_PYTHON; python3.13…python3.10, python3, python on PATH
 * (Windows: `py -3.13`…`py -3.10` first); then common Homebrew / Anaconda / Miniconda locations.
 * Returns { version, parsed, executable, source } or exits with instructions.
 */
export function findPython({ quiet = false } = {}) {
  const env = mergedEnv();
  const tried = [];
  if (env.APP_PYTHON) {
    const found = probePython(env.APP_PYTHON);
    if (!found) fail(`APP_PYTHON is set to "${env.APP_PYTHON}", but that command does not run Python.\n  Fix the path, or unset APP_PYTHON to let App Creator search.`);
    if (!isSupportedPython(found.parsed)) fail(`APP_PYTHON points to Python ${found.version}; App Creator needs Python ${SUPPORTED_RANGE}.`);
    return { ...found, source: 'APP_PYTHON' };
  }
  const minors = [];
  for (let m = PYTHON_MAX[1]; m >= PYTHON_MIN[1]; m--) minors.push(`3.${m}`);
  const candidates = [];
  if (IS_WIN) for (const v of minors) candidates.push(['py', [`-${v}`]]);
  for (const v of minors) candidates.push([IS_WIN ? `python${v}` : `python${v}`, []]);
  candidates.push(['python3', []], ['python', []]);
  const home = os.homedir();
  const condaRoots = [
    path.join(home, 'anaconda3'), path.join(home, 'opt', 'anaconda3'), path.join(home, 'miniconda3'),
    path.join(home, 'opt', 'miniconda3'), path.join(home, 'miniforge3'),
    '/opt/anaconda3', '/opt/miniconda3', '/opt/homebrew/anaconda3', '/opt/homebrew/Caskroom/miniconda/base',
    'C:\\ProgramData\\anaconda3', 'C:\\ProgramData\\miniconda3',
  ];
  if (!IS_WIN) {
    for (const dir of ['/opt/homebrew/bin', '/usr/local/bin', '/usr/bin']) {
      for (const v of minors) candidates.push([path.join(dir, `python${v}`), []]);
    }
  }
  for (const root of condaRoots) {
    candidates.push([IS_WIN ? path.join(root, 'python.exe') : path.join(root, 'bin', 'python3'), []]);
  }
  for (const [cmd, args] of candidates) {
    if (path.isAbsolute(cmd) && !fs.existsSync(cmd)) continue;
    const found = probePython(cmd, args);
    const label = [cmd, ...args].join(' ');
    if (!found) continue;
    if (isSupportedPython(found.parsed)) {
      if (!quiet && tried.length) console.log(c.dim(`  (skipped: ${tried.join(', ')})`));
      return { ...found, source: label };
    }
    tried.push(`${label} = ${found.version}`);
  }
  fail(`no supported Python found. App Creator needs Python ${SUPPORTED_RANGE}.\n` +
    (tried.length ? `  Found only: ${tried.join('; ')}.\n` : '') +
    '  Install one (python.org, Homebrew `brew install python@3.12`, or `conda create -n app python=3.12`),\n' +
    '  then either open a new terminal, or tell App Creator exactly which one to use:\n' +
    '    macOS/Linux:  APP_PYTHON=/path/to/python3.12 npm run setup\n' +
    '    Windows:      set APP_PYTHON=C:\\path\\to\\python.exe   then   npm run setup\n' +
    '  (or put APP_PYTHON=... in the root .env file).');
}

/** Path of the Python inside a virtual environment. */
export function venvPython(backendDir) {
  return IS_WIN ? path.join(backendDir, '.venv', 'Scripts', 'python.exe') : path.join(backendDir, '.venv', 'bin', 'python');
}

// ---------------------------------------------------------------- hashing / stamps

export function sha256File(...files) {
  const h = createHash('sha256');
  for (const f of files) h.update(fs.existsSync(f) ? fs.readFileSync(f) : `missing:${f}`);
  return h.digest('hex');
}

export function sha256(text) {
  return createHash('sha256').update(text).digest('hex');
}

const STAMP_DIR = path.join(CACHE_DIR, 'setup');

/** Setup stamps: one small file per (step, directory) that stores the hash of the inputs last installed. */
export function readStamp(step, dir) {
  const f = path.join(STAMP_DIR, `${step}-${sha256(dir).slice(0, 12)}.json`);
  try { return JSON.parse(fs.readFileSync(f, 'utf8')).hash; } catch { return null; }
}

export function writeStamp(step, dir, hash) {
  fs.mkdirSync(STAMP_DIR, { recursive: true });
  const f = path.join(STAMP_DIR, `${step}-${sha256(dir).slice(0, 12)}.json`);
  fs.writeFileSync(f, JSON.stringify({ step, dir, hash, at: new Date().toISOString() }, null, 2));
}

// ---------------------------------------------------------------- commands

/**
 * How to run npm without a shell: under `npm run`, npm tells us its own CLI script (npm_execpath), which we
 * run with the current Node. Otherwise fall back to `npm` (through the shell on Windows, where it is npm.cmd).
 */
export function npmCommand(args) {
  const cli = process.env.npm_execpath;
  const display = ['npm', ...args];
  if (cli && /npm-cli\.js$/.test(cli) && fs.existsSync(cli)) return { cmd: process.execPath, args: [cli, ...args], shell: false, display };
  return { cmd: 'npm', args, shell: IS_WIN, display };
}

/**
 * Runs a package's own CLI from <dir>/node_modules with the current Node (no npx, no shell, no download).
 * Falls back to `npx --no-install` if the package layout is unexpected.
 */
export function localBin(dir, pkg, bin, args) {
  try {
    const pkgDir = path.join(dir, 'node_modules', ...pkg.split('/'));
    const meta = JSON.parse(fs.readFileSync(path.join(pkgDir, 'package.json'), 'utf8'));
    const rel = typeof meta.bin === 'string' ? meta.bin : meta.bin?.[bin];
    if (rel) return { cmd: process.execPath, args: [path.join(pkgDir, rel), ...args], shell: false, display: [bin, ...args] };
  } catch { /* fall through */ }
  return { cmd: 'npx', args: ['--no-install', bin, ...args], shell: IS_WIN, display: [bin, ...args] };
}

function quoteForShell(a) {
  return /[\s"&|<>^]/.test(a) ? `"${a.replace(/"/g, '\\"')}"` : a;
}

function spawnSpec(spec) {
  if (spec.shell) return [[spec.cmd, ...spec.args].map(quoteForShell).join(' '), [], true];
  return [spec.cmd, spec.args, false];
}

/** Text written to a log stream (if any) and the terminal. */
export function makeTee(logStream) {
  return {
    out: (chunk) => { process.stdout.write(chunk); logStream?.write(chunk); },
    err: (chunk) => { process.stderr.write(chunk); logStream?.write(chunk); },
    note: (text) => { console.log(text); logStream?.write(`${text}\n`); },
  };
}

/**
 * Runs a command to completion, streaming its output. Resolves to the exit code (never rejects for a nonzero
 * exit). `spec` is { cmd, args, shell } (see npmCommand / localBin) or built with cmdSpec().
 */
export function run(spec, { cwd = REPO_ROOT, env = mergedEnv(), log } = {}) {
  const tee = makeTee(log);
  const [cmd, args, shell] = spawnSpec(spec);
  const shown = spec.display || [spec.cmd === process.execPath ? 'node' : spec.cmd, ...spec.args];
  const short = (a) => (path.isAbsolute(a) && a.startsWith(REPO_ROOT) ? path.relative(cwd, a) || a : a);
  tee.note(c.dim(`$ ${shown.map(short).join(' ')}  (in ${path.relative(REPO_ROOT, cwd) || '.'})`));
  return new Promise((resolve) => {
    const child = spawn(cmd, args, { cwd, env, shell, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
    child.stdout.on('data', tee.out);
    child.stderr.on('data', tee.err);
    child.on('error', (err) => { tee.err(`${err.message}\n`); resolve(127); });
    child.on('close', (code, signal) => resolve(code ?? (signal ? 1 : 0)));
  });
}

export const cmdSpec = (cmd, args = []) => ({ cmd, args, shell: false });

// ---------------------------------------------------------------- long-running services

const services = new Set();
let cleanupInstalled = false;
let stopping = false;

/** True once a stop was requested (Ctrl+C or stopServices), so exits are expected, not crashes. */
export const isStopping = () => stopping;

/** Kills one of OUR children together with everything it started (its process group / process tree). */
function killTree(child, signal = 'SIGTERM') {
  if (!child.pid) return;
  try {
    if (IS_WIN) {
      // taskkill /T needs the parent alive to find the tree; only our own child's pid is ever passed.
      if (child.exitCode === null && child.signalCode === null) {
        spawnSync('taskkill', ['/PID', String(child.pid), '/T', '/F'], { stdio: 'ignore', windowsHide: true });
      }
    } else {
      // Our child leads its own process group (detached), so -pid reaches its helpers even if it already exited.
      process.kill(-child.pid, signal);
    }
  } catch { /* group already gone */ }
}

function installCleanup() {
  if (cleanupInstalled) return;
  cleanupInstalled = true;
  process.on('exit', () => { for (const s of services) killTree(s.child, 'SIGKILL'); });
  for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) {
    process.on(sig, async () => {
      if (stopping) return;
      stopping = true;
      console.log(`\n${c.yellow(`Stopping (${sig})…`)}`);
      await stopServices();
      process.exit(130);
    });
  }
}

/**
 * Starts a long-running child (a server) in its own process group, prefixing its output lines with [name].
 * Returns a handle { name, child, exited } where `exited` is a promise of the exit code.
 */
export function startService(name, spec, { cwd, env, log } = {}) {
  installCleanup();
  const tee = makeTee(log);
  const [cmd, args, shell] = spawnSpec(spec);
  const child = spawn(cmd, args, { cwd, env, shell, detached: !IS_WIN, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
  const prefix = c.dim(`[${name}] `);
  const pipe = (write) => {
    let buf = '';
    return (chunk) => {
      buf += chunk.toString();
      const lines = buf.split(/\r?\n/);
      buf = lines.pop();
      for (const line of lines) write(`${prefix}${line}\n`);
    };
  };
  child.stdout.on('data', pipe(tee.out));
  child.stderr.on('data', pipe(tee.err));
  const handle = { name, child };
  handle.exited = new Promise((resolve) => {
    child.on('error', (err) => { tee.err(`${prefix}${err.message}\n`); resolve(127); });
    child.on('exit', (code, signal) => resolve(code ?? (signal ? 1 : 0)));
  });
  services.add(handle);
  return handle;
}

/** Stops every service started by this process: polite signal first, forced after a short grace period. */
export async function stopServices(graceMs = 4000) {
  const list = [...services];
  for (const s of list) killTree(s.child, 'SIGTERM');
  await Promise.race([Promise.all(list.map((s) => s.exited)), sleep(graceMs)]);
  for (const s of list) killTree(s.child, 'SIGKILL');
  await Promise.race([Promise.all(list.map((s) => s.exited)), sleep(1000)]);
  for (const s of list) services.delete(s);
}

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Waits until `url` answers with a status below 500. Gives up early if `service` exits.
 * Returns true on success, false on timeout or early exit.
 */
export async function waitForUrl(url, { timeoutMs = 90000, service } = {}) {
  let exited = false;
  service?.exited.then(() => { exited = true; });
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline && !exited) {
    try {
      const res = await fetch(url, { signal: AbortSignal.timeout(5000) });
      if (res.status < 500) return true;
    } catch { /* not up yet */ }
    await sleep(500);
  }
  return false;
}

// ---------------------------------------------------------------- ports

/** True if nothing is listening on 127.0.0.1:<port> (checked by briefly listening ourselves). */
export function isPortFree(port) {
  return new Promise((resolve) => {
    const srv = net.createServer();
    srv.once('error', () => resolve(false));
    srv.once('listening', () => srv.close(() => resolve(true)));
    srv.listen({ port, host: '127.0.0.1', exclusive: true });
  });
}

/** Exits with a clear message if the port is taken. Never touches the process that holds it. */
export async function requireFreePort(port, envName, what) {
  if (await isPortFree(port)) return;
  fail(`port ${port} (${what}) is already in use on 127.0.0.1.\n` +
    '  App Creator does not stop other programs. Either close the program using it (maybe an earlier\n' +
    '  `npm run dev` in another terminal), or pick another port, for example:\n' +
    `    macOS/Linux:  ${envName}=${port + 1} npm run dev\n` +
    `    Windows:      set ${envName}=${port + 1}   then   npm run dev\n` +
    `  (or set ${envName} in the root .env file).`);
}

/** First free port at or after `start`, skipping any in `exclude`. */
export async function findFreePort(start, exclude = []) {
  for (let p = start; p < start + 200; p++) {
    if (!exclude.includes(p) && (await isPortFree(p))) return p;
  }
  fail(`no free port found between ${start} and ${start + 199}.`);
}

// ---------------------------------------------------------------- files

const COPY_SKIP = new Set(['node_modules', '.venv', '.next', '.next-verify', 'test-results', 'playwright-report',
  '__pycache__', '.pytest_cache', '.ruff_cache', '.DS_Store', 'next-env.d.ts']);

/** Copies a source tree without build output, caches or installed dependencies. */
export function copyTree(src, dest) {
  fs.cpSync(src, dest, {
    recursive: true,
    filter: (p) => !COPY_SKIP.has(path.basename(p)) && !p.endsWith('.tsbuildinfo'),
  });
}

/** Formats seconds for the summary table. */
export const secs = (ms) => (ms / 1000).toFixed(1);
