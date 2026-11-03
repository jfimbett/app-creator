#!/usr/bin/env node
// Redact home-directory paths (personal data: the OS user name) in tracked step records and progress notes,
// using the explicit marker [REDACTED:user]. Content is otherwise unchanged.
//   node scripts/redact-records.mjs [--check]
// --check only reports files that still contain a home path (exit 1 if any).
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';

const HOME = /(\/Users\/|\/home\/|C:\\Users\\)(?![[<])[^/\\\s"'`)<>[\]]+/g;
const check = process.argv.includes('--check');
const files = execFileSync('git', ['ls-files', 'runs', 'PROGRESS.md', 'docs'], { encoding: 'utf8' })
  .split('\n').filter(Boolean);
let hits = 0;
for (const f of files) {
  const text = readFileSync(f, 'utf8');
  const out = text.replace(HOME, '$1[REDACTED:user]');
  if (out !== text) {
    hits++;
    if (check) console.log(`home path in ${f}`);
    else { writeFileSync(f, out); console.log(`redacted ${f}`); }
  }
}
console.log(`${hits} file(s) ${check ? 'with home paths' : 'redacted'}`);
process.exit(check && hits ? 1 : 0);
