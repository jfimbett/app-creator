# PROMPT — B10-interview-questions

- Sender: owner (top-level Claude Code session)
- Receiver: product-architect (agent created in B06; interviewer role)
- Starting commit at prompt write: 14c2d39 (RESULT.json records the commit at dispatch)
- Skills to load: product-interview (delegated mode)
- Key instruction/reference files (sha256 prefix when written):
  - docs/TOOLKIT.md cde60522bfd2ce4b
  - GOAL.md 20b3a7b8e8c2aa44
  - docs/research/sec-edgar.md 20e133591605db35
  - docs/research/openrouter.md 94799b2d9612e152
  - .claude/skills/product-interview/SKILL.md a188d28441e36165
- Dispatch: `node scripts/dispatch-step.mjs --step runs/bootstrap/B10-interview-questions --agent product-architect --mode bypassPermissions --milestone bootstrap`

<!-- DISPATCH:BEGIN -->
Task B10 of the App Creator bootstrap: run the product interview for the SEC Analytics example in **delegated mode**, step 1 of 3 (questions only). Load and follow `.claude/skills/product-interview/SKILL.md` (Delegated mode section) and its templates. Context: the product owner is the course instructor, who has written the complete brief GOAL.md and explicitly delegated routine product decisions (GOAL.md §8 "Mandatory supervisor, product-owner role"). The `delegated-product-owner` agent will answer your questions in the next step; you will then write the documents in step 3. Read GOAL.md fully (it is the brief), docs/TOOLKIT.md, and docs/research/sec-edgar.md and docs/research/openrouter.md for domain facts.
Work: produce the interview questions you would ask the owner, covering every round of the skill (customers and problem, main user journey per milestone, screens and visuals including the dashboard/table choice, MVP features and exclusions per milestone, data and calculations with formulas/units, accounts/saved data/uploads/payments, team and constraints) plus the questions this product specifically needs (demo universe and fixture scope, data-source labelling, restatement/duplicate policy, metric definitions such as EBIT/EBITDA/FCF/ROE/ROA, comparisons and normalization, filing section extraction fallback, AI analyst scope/model/key handling, classroom network constraints, launch commands). Ask questions even where you believe GOAL.md answers them — the delegate will cite the answer; that keeps the record explicit. Number them Q1..Qn (aim for 30–45, grouped by round), each one sentence and answerable. Do not answer them yourself. Do not write or edit any file. Return the numbered question list in your final message, followed by the handoff.

End your final message with exactly this block (concise):
## Handoff
Changes: <files created/changed>
Verification evidence: <commands run and exit codes>
Remaining findings: <open issues, doubts>
Next action: <one line>
Do not commit, push, tag or change git configuration; the owner integrates and commits. Never read, create or print .env files or secrets, and never write email addresses into files.
<!-- DISPATCH:END -->
