// App-level tasks shared by setup.mjs, dev.mjs, demo.mjs and verify.mjs.
// An `app` is the object returned by lib.loadConfig().app or lib.resolveApp() (absolute directories).

import fs from 'node:fs';
import path from 'node:path';
import {
  BROWSERS_PATH, REPO_ROOT, c, cmdSpec, findPython, heading, localBin, mergedEnv, npmCommand, probePython,
  isSuccess, isSupportedPython, readStamp, run, sha256, sha256File, startService, venvPython, waitForUrl, writeStamp,
} from './lib.mjs';

const rel = (p) => path.relative(REPO_ROOT, p) || '.';

// ---------------------------------------------------------------- setup

/**
 * Installs everything the app needs, skipping steps whose inputs have not changed since the last run.
 * Never calls `npm run setup` (no recursion). Returns 0 on success, otherwise the failing exit code.
 */
export async function setupApp(app, { force = false, log } = {}) {
  const say = (t) => { console.log(t); log?.write(`${t}\n`); };
  const python = findPython();
  say(`Python: ${python.version} (${python.source})`);

  // 1. Backend virtual environment (recreated only if missing or not a supported/requested version).
  heading(`Backend environment (${rel(app.backendDir)}/.venv)`);
  const vpy = venvPython(app.backendDir);
  const existing = fs.existsSync(vpy) ? probePython(vpy) : null;
  const sameMinor = existing && existing.parsed[0] === python.parsed[0] && existing.parsed[1] === python.parsed[1];
  const wantsSpecific = python.source === 'APP_PYTHON';
  if (!force && existing && isSupportedPython(existing.parsed) && (sameMinor || !wantsSpecific)) {
    say(c.green(`up to date (Python ${existing.version})`));
  } else {
    if (existing || fs.existsSync(path.join(app.backendDir, '.venv'))) {
      say(`Recreating .venv (${existing ? `was Python ${existing.version}` : 'broken'}).`);
      fs.rmSync(path.join(app.backendDir, '.venv'), { recursive: true, force: true });
    }
    const code = await run(cmdSpec(python.executable, ['-m', 'venv', '.venv']), { cwd: app.backendDir, log });
    if (code) return code;
  }
  const venvInfo = probePython(vpy);
  if (!venvInfo) { say(c.red(`Could not run ${vpy}.`)); return 1; }

  // 2. Backend packages from the lock file, with the venv's own pip.
  heading('Backend packages (requirements.lock)');
  const lock = path.join(app.backendDir, 'requirements.lock');
  if (!fs.existsSync(lock)) { say(c.red(`Missing ${rel(lock)}.`)); return 1; }
  // The stamp is tied to this particular .venv (its pyvenv.cfg timestamp), so a recreated or replaced
  // environment at the same path is always reinstalled.
  const venvId = fs.statSync(path.join(app.backendDir, '.venv', 'pyvenv.cfg')).mtimeMs;
  const pipHash = sha256(`${sha256File(lock)}|${venvInfo.version}|${venvId}`);
  if (!force && readStamp('pip', app.backendDir) === pipHash) {
    say(c.green('up to date'));
  } else {
    const code = await run(cmdSpec(vpy, ['-m', 'pip', 'install', '--disable-pip-version-check', '-r', 'requirements.lock']),
      { cwd: app.backendDir, log });
    if (code) return code;
    writeStamp('pip', app.backendDir, pipHash);
  }

  // 3. Frontend packages from package-lock.json.
  heading(`Frontend packages (${rel(app.frontendDir)})`);
  const pkgLock = path.join(app.frontendDir, 'package-lock.json');
  if (!fs.existsSync(pkgLock)) { say(c.red(`Missing ${rel(pkgLock)}.`)); return 1; }
  // npm writes node_modules/.package-lock.json on every install; its timestamp ties the stamp to this node_modules.
  const installedMarker = path.join(app.frontendDir, 'node_modules', '.package-lock.json');
  const npmHash = () => sha256(`${sha256File(pkgLock)}|${process.versions.node}|${fs.existsSync(installedMarker) ? fs.statSync(installedMarker).mtimeMs : 'none'}`);
  if (!force && fs.existsSync(installedMarker) && readStamp('npm', app.frontendDir) === npmHash()) {
    say(c.green('up to date'));
  } else {
    const code = await run(npmCommand(['ci', '--no-audit', '--no-fund']), { cwd: app.frontendDir, log });
    if (code) return code;
    writeStamp('npm', app.frontendDir, npmHash());
  }

  // 4. Project-local Playwright browser (headless Chromium shell) in .cache/ms-playwright.
  heading('Browser for checks (Playwright Chromium, project-local)');
  const pwVersion = installedVersion(app.frontendDir, '@playwright/test');
  const pwHash = sha256(`${pwVersion}|${BROWSERS_PATH}|full-chromium`);
  if (!force && readStamp('playwright', BROWSERS_PATH) === pwHash && hasChromium()) {
    say(c.green(`up to date (Playwright ${pwVersion})`));
  } else {
    const code = await run(localBin(app.frontendDir, 'playwright', 'playwright', ['install', '--no-shell', 'chromium']),
      { cwd: app.frontendDir, env: mergedEnv({ PLAYWRIGHT_BROWSERS_PATH: BROWSERS_PATH }), log });
    if (code) return code;
    writeStamp('playwright', BROWSERS_PATH, pwHash);
  }
  return 0;
}

function installedVersion(dir, pkg) {
  try {
    return JSON.parse(fs.readFileSync(path.join(dir, 'node_modules', ...pkg.split('/'), 'package.json'), 'utf8')).version;
  } catch { return 'unknown'; }
}

function hasChromium() {
  try { return fs.readdirSync(BROWSERS_PATH).some((d) => /^chromium-\d+$/.test(d)); } catch { return false; }
}

/** Returns a list of human-readable problems if setup has not been run for this app. */
export function setupProblems(app) {
  const problems = [];
  if (!fs.existsSync(venvPython(app.backendDir))) problems.push(`the backend environment ${rel(app.backendDir)}/.venv does not exist`);
  if (!fs.existsSync(path.join(app.frontendDir, 'node_modules'))) problems.push(`frontend packages are not installed in ${rel(app.frontendDir)}`);
  return problems;
}

// ---------------------------------------------------------------- services

/**
 * Starts the backend (uvicorn) and the frontend (Next.js `dev` or `start`) as our own children.
 * mode: 'dev' | 'start'. Returns { backend, frontend, url } or throws with a readable message.
 */
export async function startApp(app, { backendPort, frontendPort, mode = 'dev', extraEnv = {}, distDir, log } = {}) {
  const backendUrl = `http://127.0.0.1:${backendPort}`;
  const env = mergedEnv({ ...extraEnv, BACKEND_URL: backendUrl, ...(distDir ? { NEXT_DIST_DIR: distDir } : {}) });
  const backend = startService('backend', cmdSpec(venvPython(app.backendDir),
    ['-m', 'uvicorn', app.backendApp, '--host', '127.0.0.1', '--port', String(backendPort)]), { cwd: app.backendDir, env, log });
  if (!(await waitForUrl(`${backendUrl}${app.healthPath}`, { timeoutMs: 60000, service: backend, accept: isSuccess }))) {
    throw new Error(`the backend did not answer at ${backendUrl}${app.healthPath} (see the [backend] lines above).`);
  }
  const nextArgs = mode === 'dev'
    ? ['dev', '--port', String(frontendPort), '--hostname', '127.0.0.1']
    : ['start', '--port', String(frontendPort), '--hostname', '127.0.0.1'];
  const frontend = startService('frontend', localBin(app.frontendDir, 'next', 'next', nextArgs), { cwd: app.frontendDir, env, log });
  const url = `http://127.0.0.1:${frontendPort}`;
  if (!(await waitForUrl(url, { timeoutMs: 120000, service: frontend }))) {
    throw new Error(`the frontend did not answer at ${url} (see the [frontend] lines above).`);
  }
  return { backend, frontend, url, backendUrl };
}
