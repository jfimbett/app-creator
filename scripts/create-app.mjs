// npm run create-app [-- --dir <path>] [--name "<App name>"] [--dry-run]
// Copies scaffold/ to app/ (or --dir), creates <dir>/docs/README.md and points app-creator.config.json at the
// new folders. Refuses to overwrite an existing folder or to replace an app that is already configured.
// --dry-run prints what would happen and changes nothing.
import fs from 'node:fs';
import path from 'node:path';
import { APP_DEFAULTS, REPO_ROOT, c, copyTree, fail, loadConfig, toConfigPath, writeConfig } from './lib.mjs';

const argv = process.argv.slice(2);
const option = (flag) => {
  const i = argv.indexOf(flag);
  if (i === -1) return undefined;
  const v = argv[i + 1];
  if (!v || v.startsWith('--')) fail(`${flag} needs a value.`);
  return v;
};
const dryRun = argv.includes('--dry-run');
const target = path.resolve(REPO_ROOT, option('--dir') || 'app');
const name = option('--name') || 'My App';
const PLACEHOLDER = 'My App';

const rel = toConfigPath(target);
if (rel.startsWith('..') || path.isAbsolute(rel)) fail(`--dir must be inside this repository (${REPO_ROOT}).`);
if (rel === '' || ['scaffold', 'scripts', 'docs', '.claude', '.clinerules', '.git', '.github', 'node_modules', '.cache',
  '.logs', 'runs', 'milestones'].includes(rel.split('/')[0])) {
  fail(`--dir "${rel || '.'}" would mix the app with the toolkit's own folders; choose a new folder such as app/.`);
}
// Letters of any language (Café, Łódź) are fine; double quotes and backslashes are not, because the name is
// inserted into "..." strings in the source code.
if (!/^[\p{L}\p{N}_ .'&-]{1,60}$/u.test(name)) fail('--name may use letters, digits, spaces and . \' & - _ (up to 60 characters).');
if (fs.existsSync(target)) fail(`${rel}/ already exists. create-app never overwrites; choose another --dir or remove it yourself.`);

const { raw } = loadConfig();
if (raw.app) {
  fail(`app-creator.config.json already points to an app ("${raw.app.name}" in ${raw.app.frontendDir}).\n` +
    '  create-app sets up one app per branch. Edit the config yourself if you really want to switch apps.');
}

const entry = {
  name,
  frontendDir: `${rel}/frontend`,
  backendDir: `${rel}/backend`,
  docsDir: `${rel}/docs`,
  ...structuredClone(APP_DEFAULTS),
};
const nameFiles = ['frontend/lib/site.ts', 'backend/app/main.py'];

const actions = [
  `copy scaffold/ -> ${rel}/ (without node_modules, .venv or build output)`,
  `create ${rel}/docs/README.md`,
  ...(name !== PLACEHOLDER ? nameFiles.map((f) => `set the app name "${name}" in ${rel}/${f}`) : []),
  `set "app" in app-creator.config.json to:\n${JSON.stringify(entry, null, 2).replace(/^/gm, '      ')}`,
];

if (dryRun) {
  console.log(c.bold('Dry run: nothing will be changed. create-app would:'));
  for (const a of actions) console.log(`  - ${a}`);
  process.exit(0);
}

copyTree(path.join(REPO_ROOT, 'scaffold'), target);
fs.mkdirSync(path.join(target, 'docs'), { recursive: true });
fs.writeFileSync(path.join(target, 'docs', 'README.md'), `# ${name}: project documents

This folder holds the documents for this app. The \`product-interview\` skill writes them:

- \`product.md\`: who the app is for, what the first version (MVP) does, and what it leaves out.
- \`architecture.md\`: how it is built, plus a log of the decisions made.
- \`acceptance.md\`: the checks that show each feature works.
- \`plan.md\`: the slices to build, in order, with a progress log.

The code is in \`../frontend\` (Next.js) and \`../backend\` (FastAPI). Run it from the repository root with
\`npm run setup\`, then \`npm run dev\`.
`);
if (name !== PLACEHOLDER) {
  for (const f of nameFiles) {
    const p = path.join(target, f);
    fs.writeFileSync(p, fs.readFileSync(p, 'utf8').split(PLACEHOLDER).join(name));
  }
}
raw.app = entry;
writeConfig(raw);

for (const a of actions) console.log(`${c.green('done')}  ${a.split('\n')[0]}`);
console.log(`
${c.bold(`Created ${name} in ${rel}/.`)} Next steps:
  1. npm run setup     install its packages (a few minutes the first time)
  2. npm run dev       open http://127.0.0.1:3000 and check the status panel says the backend is OK
  3. npm run verify    run every check
  4. In Claude Code, type /product-interview to describe your product; its documents go to ${rel}/docs/.`);
