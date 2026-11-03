// npm run verify  [--quick] [--skip-scaffold]
// 1. Toolkit checks (check-toolkit.mjs).
// 2. With an app configured: its checks. Without one (template): the same checks on a fresh copy of scaffold/
//    in .cache/scaffold-check/ (setup included), unless --skip-scaffold.
// App checks run in order and stop at the first failure: backend ruff + pytest; frontend lint, typecheck,
// unit tests, production build (NEXT_DIST_DIR=.next-verify); then backend + `next start` on spare ports and
// the Playwright smoke test. --quick skips the build and the browser test.
// Output is shown live and saved to .logs/verify-<timestamp>.log. Exit code is nonzero if anything failed.
import fs from 'node:fs';
import path from 'node:path';
import { setupApp, setupProblems, startApp } from './app-tasks.mjs';
import {
  BROWSERS_PATH, CACHE_DIR, REPO_ROOT, c, checkNode, cmdSpec, copyTree, findFreePort, heading, loadConfig,
  localBin, mergedEnv, npmCommand, resolveApp, run, secs, stopServices, venvPython,
} from './lib.mjs';

const argv = process.argv.slice(2);
const quick = argv.includes('--quick');
const skipScaffold = argv.includes('--skip-scaffold');
const DIST = '.next-verify';

checkNode();
fs.mkdirSync(path.join(REPO_ROOT, '.logs'), { recursive: true });
const stamp = new Date().toISOString().replace(/[:.]/g, '-');
const logPath = path.join(REPO_ROOT, '.logs', `verify-${stamp}.log`);
const log = fs.createWriteStream(logPath);

const results = [];
/** Runs one named step, records result and time. fn returns an exit code (0 = pass). */
async function step(name, fn) {
  heading(name);
  log.write(`\n== ${name}\n`);
  const t0 = Date.now();
  let code;
  try { code = await fn(); } catch (err) { console.error(c.red(err.message)); log.write(`${err.message}\n`); code = 1; }
  results.push({ name, ok: code === 0, ms: Date.now() - t0 });
  return code === 0;
}

function summary() {
  const w = Math.max(...results.map((r) => r.name.length), 4);
  const lines = ['', `${'Step'.padEnd(w)}  Result  Seconds`, `${'-'.repeat(w)}  ------  -------`];
  for (const r of results) lines.push(`${r.name.padEnd(w)}  ${r.ok ? 'pass  ' : 'FAIL  '}  ${secs(r.ms).padStart(7)}`);
  const failed = results.filter((r) => !r.ok).length;
  lines.push('', failed ? `${failed} step(s) failed.` : 'All checks passed.', `Full log: ${path.relative(REPO_ROOT, logPath)}`);
  for (const l of lines) {
    const shown = l.includes('FAIL') || l.includes('failed.') ? c.red(l) : l === 'All checks passed.' ? c.green(l) : l;
    console.log(shown);
    log.write(`${l}\n`);
  }
  return failed;
}

async function finish() {
  await stopServices();
  const failed = summary();
  await new Promise((r) => log.end(r));
  process.exit(failed ? 1 : 0);
}

/** The app checks, in order; returns false at the first failure. */
async function appChecks(app, label) {
  const be = app.backendDir;
  const fe = app.frontendDir;
  const vpy = venvPython(be);
  const npm = (script, env = {}) => () => run(npmCommand(['run', script]), { cwd: fe, env: mergedEnv(env), log });

  if (!(await step(`${label}backend lint (ruff)`, () => run(cmdSpec(vpy, ['-m', 'ruff', 'check', '.']), { cwd: be, log })))) return false;
  if (!(await step(`${label}backend tests (pytest)`, () => run(cmdSpec(vpy, ['-m', 'pytest', '-q']), { cwd: be, log })))) return false;
  if (!(await step(`${label}frontend lint`, npm('lint')))) return false;
  if (!(await step(`${label}frontend typecheck`, npm('typecheck')))) return false;
  if (!(await step(`${label}frontend unit tests`, npm('test')))) return false;
  if (quick) {
    console.log(c.dim('--quick: skipping the production build and the browser test.'));
    return true;
  }

  // Spare ports are chosen before the build because `next build` records the /api rewrite target.
  const backendPort = await findFreePort(8100);
  const frontendPort = await findFreePort(3100, [backendPort]);
  const backendUrl = `http://127.0.0.1:${backendPort}`;
  const buildEnv = { ...app.demoEnv, NEXT_DIST_DIR: DIST, BACKEND_URL: backendUrl };
  if (!(await step(`${label}frontend build`, npm('build', buildEnv)))) return false;

  return step(`${label}browser smoke test (Playwright)`, async () => {
    console.log(c.dim(`Using spare ports: backend ${backendPort}, frontend ${frontendPort} (demoEnv applied).`));
    const { url } = await startApp(app, { backendPort, frontendPort, mode: 'start', extraEnv: app.demoEnv, distDir: DIST, log });
    const spec = localBin(fe, '@playwright/test', 'playwright', ['test', ...(app.smokeSpec ? [app.smokeSpec] : [])]);
    const code = await run(spec, { cwd: fe, env: mergedEnv({ ...app.demoEnv, BASE_URL: url, PLAYWRIGHT_BROWSERS_PATH: BROWSERS_PATH, CI: '1' }), log });
    await stopServices();
    return code;
  });
}

// ---------------------------------------------------------------- main

const toolkitOk = await step('toolkit checks', () => run(cmdSpec(process.execPath, [path.join(REPO_ROOT, 'scripts', 'check-toolkit.mjs')]), { log }));
if (!toolkitOk) console.log(c.yellow('Toolkit checks failed; the app checks still run so you see every problem. Verify will exit nonzero.'));

const { app } = loadConfig();
if (app) {
  const problems = setupProblems(app);
  if (problems.length) {
    await step('setup present', () => {
      console.error(c.red(`Setup has not been run: ${problems.join('; ')}. Run \`npm run setup\` first.`));
      return 1;
    });
  } else {
    await appChecks(app, '');
  }
} else if (skipScaffold) {
  console.log(c.dim('\nNo app configured and --skip-scaffold given: only the toolkit was checked.'));
} else {
  const dir = path.join(CACHE_DIR, 'scaffold-check');
  const ok = await step('scaffold copy + setup', async () => {
    fs.rmSync(dir, { recursive: true, force: true });
    copyTree(path.join(REPO_ROOT, 'scaffold'), dir);
    console.log(`Fresh copy of scaffold/ in ${path.relative(REPO_ROOT, dir)}`);
    const scaffoldApp = resolveApp({ name: 'Scaffold check', frontendDir: 'frontend', backendDir: 'backend', docsDir: 'docs' }, dir);
    return setupApp(scaffoldApp, { log });
  });
  if (ok) {
    const scaffoldApp = resolveApp({ name: 'Scaffold check', frontendDir: 'frontend', backendDir: 'backend', docsDir: 'docs' }, dir);
    await appChecks(scaffoldApp, 'scaffold: ');
  }
}
await finish();
