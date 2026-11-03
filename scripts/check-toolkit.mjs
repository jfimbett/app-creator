// npm run check-toolkit
// Static checks of the toolkit itself (no network, no installs):
//   - every .claude/skills/<name>/SKILL.md has frontmatter, name == folder, description non-empty and <= 1024 chars
//   - every .claude/agents/<name>.md has name == file name and a description
//   - .claude/skills/INDEX.md (if present) mentions every skill folder
//   - relative markdown links in the repository's *.md files resolve (http(s), mailto and #anchors ignored;
//     node_modules, .venv and runs/ skipped; tracked and untracked-but-not-ignored files are checked)
//   - if milestones/ exists, each milestones/0*/ has a PROMPT.md
//   - no .env file other than .env.example is tracked by git
//   - app-creator.config.json is valid JSON with "app" null or an object
// Warnings (not failures): skills without supporting guides next to SKILL.md.
// Exit code 1 if any check failed.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { CONFIG_PATH, REPO_ROOT, c } from './lib.mjs';

const failures = [];
const warnings = [];
const passes = [];
const relp = (p) => path.relative(REPO_ROOT, p).split(path.sep).join('/');

/** Minimal YAML-frontmatter reader: top-level `key: value`, quoted values, and `>` / `|` block scalars. */
export function parseFrontmatter(text) {
  const m = text.replace(/^﻿/, '').match(/^---\r?\n([\s\S]*?)\r?\n---\s*(?:\r?\n|$)/);
  if (!m) return null;
  const data = {};
  const lines = m[1].split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const kv = lines[i].match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!kv) continue;
    let value = kv[2].trim();
    if (/^[>|][+-]?$/.test(value)) {
      const block = [];
      while (i + 1 < lines.length && (/^\s+\S/.test(lines[i + 1]) || lines[i + 1].trim() === '')) block.push(lines[++i].trim());
      value = value.startsWith('>') ? block.join(' ').replace(/\s+/g, ' ').trim() : block.join('\n').trim();
    } else if (/^"(.*)"$/.test(value)) {
      value = value.slice(1, -1).replace(/\\"/g, '"');
    } else if (/^'(.*)'$/.test(value)) {
      value = value.slice(1, -1).replace(/''/g, "'");
    }
    data[kv[1]] = value;
  }
  return data;
}

function git(args) {
  try {
    return execFileSync('git', args, { cwd: REPO_ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
  } catch { return null; }
}

// ---------------------------------------------------------------- skills

const skillsDir = path.join(REPO_ROOT, '.claude', 'skills');
const skillFolders = fs.existsSync(skillsDir)
  ? fs.readdirSync(skillsDir, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name).sort()
  : [];
for (const folder of skillFolders) {
  const file = path.join(skillsDir, folder, 'SKILL.md');
  const where = relp(file);
  if (!fs.existsSync(file)) { failures.push(`${where}: missing`); continue; }
  const fm = parseFrontmatter(fs.readFileSync(file, 'utf8'));
  if (!fm) { failures.push(`${where}: no YAML frontmatter (--- name/description ---) at the top`); continue; }
  const before = failures.length;
  if (fm.name !== folder) failures.push(`${where}: name "${fm.name ?? ''}" must equal the folder name "${folder}"`);
  if (!fm.description) failures.push(`${where}: description is missing or empty`);
  else if (fm.description.length > 1024) failures.push(`${where}: description is ${fm.description.length} characters (limit 1024)`);
  if (failures.length === before) passes.push(`skill ${folder}`);
  const extras = fs.readdirSync(path.join(skillsDir, folder)).filter((f) => f !== 'SKILL.md');
  if (!extras.length) warnings.push(`${where}: no supporting guides next to SKILL.md`);
}

const indexFile = path.join(skillsDir, 'INDEX.md');
if (fs.existsSync(indexFile)) {
  const index = fs.readFileSync(indexFile, 'utf8');
  const missing = skillFolders.filter((s) => !new RegExp(`(^|[^\\w-])${s.replace(/[-]/g, '\\-')}([^\\w-]|$)`).test(index));
  if (missing.length) failures.push(`.claude/skills/INDEX.md does not mention: ${missing.join(', ')}`);
  else passes.push('skills index lists every skill');
}

// ---------------------------------------------------------------- agents

const agentsDir = path.join(REPO_ROOT, '.claude', 'agents');
if (fs.existsSync(agentsDir)) {
  for (const f of fs.readdirSync(agentsDir).filter((x) => x.endsWith('.md')).sort()) {
    const where = `.claude/agents/${f}`;
    const fm = parseFrontmatter(fs.readFileSync(path.join(agentsDir, f), 'utf8'));
    const base = f.replace(/\.md$/, '');
    if (!fm) { failures.push(`${where}: no YAML frontmatter`); continue; }
    const before = failures.length;
    if (fm.name !== base) failures.push(`${where}: name "${fm.name ?? ''}" must equal the file name "${base}"`);
    if (!fm.description) failures.push(`${where}: description is missing or empty`);
    if (failures.length === before) passes.push(`agent ${base}`);
  }
}

// ---------------------------------------------------------------- markdown links

const SKIP_DIRS = /(^|\/)(node_modules|\.venv|runs|\.cache|\.git|\.next|\.next-verify)(\/|$)/;
const listed = git(['ls-files', '-co', '--exclude-standard', '--', '*.md']);
const mdFiles = (listed ?? '').split('\n').filter((f) => f && !SKIP_DIRS.test(f) && fs.existsSync(path.join(REPO_ROOT, f)));
let linkCount = 0;
const brokenBefore = failures.length;
for (const f of mdFiles) {
  const text = fs.readFileSync(path.join(REPO_ROOT, f), 'utf8')
    .replace(/^(```|~~~)[\s\S]*?^\1/gm, '') // fenced code blocks
    .replace(/`[^`\n]*`/g, ''); // inline code
  const re = /!?\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+["'(][^)]*)?\)/g;
  let m;
  while ((m = re.exec(text))) {
    const target = m[1];
    if (/^([a-z][a-z0-9+.-]*:|#|\/\/)/i.test(target) || /[{}<>]/.test(target)) continue;
    const clean = decodeURIComponent(target.split('#')[0].split('?')[0]);
    if (!clean) continue;
    linkCount++;
    const resolved = clean.startsWith('/') ? path.join(REPO_ROOT, clean) : path.resolve(REPO_ROOT, path.dirname(f), clean);
    if (!fs.existsSync(resolved)) failures.push(`${f}: broken link "${target}"`);
  }
}
if (listed === null) warnings.push('git is not available: markdown links were not checked');
else if (failures.length === brokenBefore) passes.push(`markdown links (${linkCount} relative links in ${mdFiles.length} files)`);

// ---------------------------------------------------------------- milestones

const msDir = path.join(REPO_ROOT, 'milestones');
if (fs.existsSync(msDir)) {
  const ms = fs.readdirSync(msDir, { withFileTypes: true }).filter((d) => d.isDirectory() && d.name.startsWith('0'));
  const missing = ms.filter((d) => !fs.existsSync(path.join(msDir, d.name, 'PROMPT.md'))).map((d) => d.name);
  if (missing.length) failures.push(`milestones without PROMPT.md: ${missing.join(', ')}`);
  else passes.push(`milestone prompts (${ms.length})`);
}

// ---------------------------------------------------------------- secrets

const tracked = git(['ls-files']);
if (tracked !== null) {
  const envFiles = tracked.split('\n').filter((f) => /^\.env(\..+)?$/.test(path.posix.basename(f)) && path.posix.basename(f) !== '.env.example');
  if (envFiles.length) failures.push(`.env files are tracked by git (remove them with \`git rm --cached\` and revoke any keys inside): ${envFiles.join(', ')}`);
  else passes.push('no .env files tracked');
}

// The project permissions must keep blocking .env reads/edits and destructive git commands.
// (Guard added after an unexplained rewrite emptied these lists during the bootstrap; see PROGRESS.md.)
try {
  const settings = JSON.parse(fs.readFileSync(path.join(REPO_ROOT, '.claude', 'settings.json'), 'utf8'));
  const deny = settings?.permissions?.deny ?? [];
  const required = ['Read(./.env)', 'Read(./**/.env)', 'Edit(/**/.env)', 'Bash(git push --force *)'];
  const absent = required.filter((r) => !deny.includes(r));
  if (absent.length) failures.push(`.claude/settings.json: required deny rules missing: ${absent.join(', ')}`);
  else passes.push('.claude/settings.json keeps .env and force-push deny rules');
} catch (err) {
  failures.push(`.claude/settings.json: ${err.code === 'ENOENT' ? 'missing' : `invalid JSON (${err.message})`}`);
}

// ---------------------------------------------------------------- config

try {
  const cfg = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  if (!('app' in cfg) || (cfg.app !== null && typeof cfg.app !== 'object')) failures.push('app-creator.config.json: "app" must be null or an object');
  else if (cfg.app && !['name', 'frontendDir', 'backendDir'].every((k) => cfg.app[k])) failures.push('app-creator.config.json: "app" needs name, frontendDir and backendDir');
  else passes.push(`config (${cfg.app ? `app "${cfg.app.name}"` : 'template: no app'})`);
} catch (err) {
  failures.push(`app-creator.config.json: ${err.code === 'ENOENT' ? 'missing' : `invalid JSON (${err.message})`}`);
}

// ---------------------------------------------------------------- report

console.log(c.bold('Toolkit check'));
for (const p of passes) console.log(`  ${c.green('ok')}    ${p}`);
for (const w of warnings) console.log(`  ${c.yellow('warn')}  ${w}`);
for (const f of failures) console.log(`  ${c.red('FAIL')}  ${f}`);
console.log(`\n${passes.length} ok, ${warnings.length} warning(s), ${failures.length} failure(s).`);
process.exit(failures.length ? 1 : 0);
