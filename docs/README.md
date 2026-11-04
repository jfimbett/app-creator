# docs/: App Creator's own documentation

This folder documents **App Creator itself**: how the toolkit is organised, what was researched to build it, and
how to use it with a team. It does **not** hold your app's documents.

## Your app's documents live elsewhere

A new app's product documents (`product.md`, `architecture.md`, `acceptance.md`, `plan.md`) go in the app's docs
folder, set by `app.docsDir` in `app-creator.config.json`. After `npm run create-app` that is **`app/docs/`**. The
`product-interview` skill writes them; the other skills keep them current.

## Index

| Document | For | What it says |
|---|---|---|
| [TOOLKIT.md](TOOLKIT.md) | anyone changing or extending the toolkit | layout, standard stack, root-command contract, working modes, step records, skill and agent names |
| [GITHUB-COLLABORATION.md](GITHUB-COLLABORATION.md) | teams of about five | roles, branches, pull requests, reviews, conflicts, suggested protections |
| [research/claude-code-and-cline.md](research/claude-code-and-cline.md) | maintainers | how Claude Code and Cline load rules, skills, agents and permissions (sources dated) |
| [research/stack-versions.md](research/stack-versions.md) | maintainers | the stack's versions and why they were chosen |
| [research/sec-edgar.md](research/sec-edgar.md) | the SEC Analytics example | SEC EDGAR data access notes |
| [research/openrouter.md](research/openrouter.md) | the SEC Analytics example | OpenRouter (AI model API) notes |

Elsewhere: [README.md](../README.md) (overview), [START-HERE.md](../START-HERE.md) (step-by-step guide),
[PROMPTS.md](../PROMPTS.md) (prompt sheet), [.claude/skills/INDEX.md](../.claude/skills/INDEX.md) (skills and agents).

## Added with the example

These documents arrive with the SEC Analytics example on `main`; they are not on the `template` branch:

- [SETUP.md](SETUP.md): tested install and run commands, offline and live modes, the SEC contact, troubleshooting.
- `ARCHITECTURE.md`: the example's frontend, backend and external-service boundaries, with a diagram.
- `TEACHING-GUIDE.md`: instructor rehearsal, checkout commands, a short demo per milestone, exercises.
- `CHANGELOG.md`: what each milestone added and what does not work.
- `FINAL-VERIFICATION.md`, `PROMPT-EXECUTION-LOG.md`, `SOURCES.md`: final checks, prompt provenance, sources.
