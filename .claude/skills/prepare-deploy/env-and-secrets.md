# Settings, environments and secrets

Companion to [SKILL.md](SKILL.md). A **setting** is a value the app reads from its environment instead of its
code (a port, a mode, a URL). A **secret** is a setting that grants access (an API key, a session secret, a
webhook secret, a database password). Secrets are never written into the repository, the chat, logs, screenshots,
fixtures or URLs.

## Where settings live

| File | Committed? | Contains | Who edits it |
|---|---|---|---|
| `.env.example` (repository root) | yes | every setting name, a comment, a safe default or a placeholder | the assistant and the team |
| `.env` (repository root) | **never** (git-ignored) | the person's real values | the person only, created with `cp .env.example .env` |
| the host's dashboard / CI settings | no | production values, set by the owner | the owner |

The root launchers (`npm run dev`, `demo`, `verify`) read the root `.env` and pass it to the backend and frontend;
values set in the terminal win over `.env`. An assistant never creates, reads, edits or prints `.env`, and never
asks anyone to paste a key into the chat. Its own runs pass non-secret settings inline:
`DATA_MODE=fixtures npm run dev`.

## Writing `.env.example`

```bash
# Data source: "fixtures" (offline recorded samples, no key needed) or "live" (needs STATS_API_KEY).
# DATA_MODE=fixtures

# Key for the statistics API, from the provider's dashboard. Leave empty for fixture mode.
# STATS_API_KEY=

# Origin of the web frontend, used for CORS and the CSRF check.
# APP_ORIGIN=http://127.0.0.1:3000

# Debug pages with details. Never on outside your own computer.
# DEBUG=0
```

Rules:

- Safe defaults: the app starts with no `.env` at all, in fixture mode, debug off.
- Placeholders are empty or obviously fake (`replace-me`); never a real key "as an example".
- Load settings in one place (for example `<backend>/app/config.py` with Pydantic or plain `os.environ`), validate
  them at start-up, and fail with a message that names the missing or invalid setting, never its value.
- Frontend: only values that are safe for every visitor may use `NEXT_PUBLIC_` (it is copied into the JavaScript
  bundle). API keys never do; the browser calls `/api/*` and the backend holds the key.
- Tests never need `.env`: they set what they need with `monkeypatch.setenv` or inline values.

## Per-environment settings

| Environment | Where values come from | Typical values |
|---|---|---|
| development | root `.env` (optional) | `DEBUG=1`, `DATA_MODE=live` or `fixtures`, local origins |
| demo / verify | the config's `demoEnv` | `DATA_MODE=fixtures`, no keys, no network |
| CI | the workflow file (no secrets) | same as demo |
| production (owner's host) | host dashboard | `DEBUG=0`, real origin, production secrets different from development ones |

Use different keys per environment where the provider allows it, so a leaked development key does not open
production. The code refuses dangerous combinations: debug on with a non-local host; a development secret outside
development; a live payment key outside production.

## Rotation

Rotating means replacing a secret with a new one and revoking the old one.

1. Create the new key in the provider's dashboard (the owner).
2. Put it where the app reads it (`.env` locally, the host's dashboard in production) and restart.
3. Check the feature works (one live call by the owner).
4. Revoke the old key in the provider's dashboard.
5. Record the date (not the key) in `<docs>/plan.md`.

Rotate after a leak, when a team member with access leaves, and on the provider's recommended schedule. A session
secret rotation signs everyone out; say so before doing it.

## If a secret leaked (committed, pasted, logged or shown on screen)

1. **Revoke it first** in the provider's dashboard and create a new one (the owner). Deleting the line or the
   commit does not help: anyone who saw the repository, a fork, CI logs or a chat may have it.
2. Remove it from the current files and replace the code with a setting read from the environment.
3. Check usage and bills in the provider's dashboard for unexpected activity.
4. Rewriting git history is **not** the default and needs the owner's explicit decision (it breaks every clone);
   revocation is what makes the old key harmless. If the repository is public, the owner may also contact the
   provider's support.
5. Record what happened, without the key, in `<docs>/plan.md` and `AI-USAGE.md` if an assistant was involved.

An assistant that notices a possible secret tells the owner immediately, without repeating the value.

## Search for leaked secrets

Run these at the repository root and report the commands (not any values found):

```bash
git ls-files | grep -iE '(^|/)\.env($|\.)' | grep -v '\.env\.example$'   # tracked env files: should print nothing
git grep -niIE '(api[_-]?key|secret|token|password)[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"']{8,}' -- ':!*.lock' ':!*package-lock.json'
git log -p --all -S 'sk_live' --oneline | head                           # repeat with the provider's key prefix
```

`git grep` finds suspicious assignments in tracked files (case-insensitive; `[[:space:]]` because git's regular
expressions do not support `\s` everywhere). These commands were run on this toolkit (macOS, zsh) and the pattern
was checked against a fake sample; on Windows, run them in Git Bash; review each hit (placeholders and test values are
fine). `git log -S` searches the history for a string. A dedicated scanner (for example gitleaks) is more thorough;
install it only with the owner's agreement.
