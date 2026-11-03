// npm run setup  [--force]
// Checks Node and Python. With an app configured: creates the backend .venv, installs requirements.lock,
// runs `npm ci` in the frontend and installs the project-local Playwright Chromium. Idempotent: steps whose
// lock files have not changed print "up to date". --force redoes every step. Never runs `npm run setup`.
import { setupApp } from './app-tasks.mjs';
import { printTemplateGuidance } from './guidance.mjs';
import { c, checkNode, fail, findPython, heading, loadConfig } from './lib.mjs';

const force = process.argv.includes('--force');

heading('Checking tools');
console.log(`Node: ${checkNode()}`);
const { app } = loadConfig();

if (!app) {
  const py = findPython();
  console.log(`Python: ${py.version} (${py.source})`);
  console.log(c.green('Node and Python are ready.'));
  printTemplateGuidance('setup');
  process.exit(0);
}

console.log(`App: ${app.name}`);
const code = await setupApp(app, { force });
if (code) fail(`setup stopped (exit code ${code}). Read the output above; fix the cause and run \`npm run setup\` again.`, code);
console.log(`\n${c.green('Setup complete.')} Next: npm run dev   (or npm run verify to run every check)`);
