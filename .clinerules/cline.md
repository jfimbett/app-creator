# Cline only

The shared rules are in `AGENTS.md` (Cline reads it). Follow them; this file only adds what differs in Cline.

- **Skills** are the folders in `.claude/skills/`. Cline's documentation lists `.claude/skills/` as a project skills
  folder, so they should appear when the student types `/`. If a skill is not offered, open
  `.claude/skills/<name>/SKILL.md` and follow it exactly.
- **Reviewers:** Cline's VS Code extension has no subagents. Follow "Without subagents" in
  `.claude/skills/review-changes/SKILL.md`: preferably one new task per reviewer, using the review prompt in
  `PROMPTS.md`. As a reviewer, never edit a file; ask before every command and run only read-only ones (`git show`,
  `git diff`, the test command). Never call a review done in this same conversation "independent".
- **Plan and Act:** plan in **Plan** mode; switch to **Act** only after the student agrees with the plan. Plan mode
  does not edit files, but it can still propose commands (seen in the instructor's rehearsal with Cline 4.1.26): in
  Plan mode propose only read-only commands, and say what each one does.
- **Python:** before creating `app/.venv`, follow "Setting up the environment" in
  `.claude/skills/product-interview/stacks.md`, including the **Anaconda / Miniconda** check: most students have
  Anaconda, and it is often not on the terminal's PATH. Use the full path of the interpreter you choose.
- **Permissions:** Cline has no per-command allow list. Ask before every command that installs, deletes, starts
  a server or changes git, even if auto-approve would let you run it.
- **Secrets:** never open, mention with `@`, `cat`, print or edit `.env` files. `.clineignore` only keeps them out
  of automatic context; it does not stop a command from reading them. The API key for the model lives in Cline's
  settings, never in this folder.
