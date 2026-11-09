# Setup

The commands below were run on macOS (Node 22.14, Python 3.10.16) on 2026-11-04. Windows is untested.

## Install and run (from the repository root)

```bash
npm ci           # once: the launcher's lockfile
npm run setup    # backend and frontend packages, project-local browser
npm run demo     # offline demo on recorded data: http://127.0.0.1:3000
npm run dev      # the same app with the Demo / Live selector
npm run verify   # every offline check
```

Ports 3000 and 8000 are refused if something else uses them. Choose others:

```bash
FRONTEND_PORT=3200 BACKEND_PORT=8200 npm run dev   # then open http://127.0.0.1:3200
```

## SEC Analytics: live SEC mode

`npm run demo` never contacts SEC. `npm run dev` offers a **Data source** selector in the header that starts on Demo.
Choosing **Live** sends requests to SEC through this app's backend; the browser only talks to your own machine.

**Set your contact first.** SEC asks automated clients to identify themselves. Create a `.env` file in the repository
root (it is git-ignored, so it is never committed) with one line:

```text
SEC_USER_AGENT=<a descriptive name> <your own contact email>
```

Each person uses their own email. Without this line, Live shows "Live SEC data is not configured" and Demo keeps working.
Restart `npm run dev` after changing the file.

**What the app does to be a good SEC citizen.** At most 1 request per second from one running app, one at a time, a 20-second
timeout, waiting when SEC asks with `Retry-After` (up to 30 seconds, two retries), and no retry after a refusal (403).
Answers are kept on disk for 24 hours (`examples/sec-analytics/backend/.cache/sec`, git-ignored) and labelled `CACHED`.
Identical requests made at the same moment share one call. Nothing is fetched in the background.

**In a classroom,** SEC's limit of 10 requests per second applies to everyone behind one public IP address. Use Demo, or
have one person use Live on a screen, rather than every student fetching at once.

**If Live fails,** the app says what happened and offers "Use recorded demo data". It never switches to demo data by itself.

**Check your live setup by hand** (3 requests; prints PASS or FAIL per check; never prints your contact):

```bash
cd examples/sec-analytics/backend
.venv/bin/python scripts/live_sec_smoke.py     # Windows (untested): .venv\Scripts\python scripts\live_sec_smoke.py
```

A browser journey through live mode is also run by hand, with `npm run dev` already running:

```bash
cd examples/sec-analytics/frontend
BASE_URL=http://127.0.0.1:3000 PLAYWRIGHT_BROWSERS_PATH=../../../.cache/ms-playwright \
  npx playwright test --config playwright.live.config.ts
```

## SEC Analytics: optional AI analyst

The analyst (from milestone M5) is optional; the rest of the app needs no key.

- **Use your own OpenRouter key with a credit limit.** Your instructor may give you a separate limited key for your
  group. Paste it in the app under Analyst → AI settings, never into a chat, a file or a commit.
- **Storage:** memory only by default (a reload forgets it). "Remember for this tab (sessionStorage)" keeps it until the
  tab closes; scripts on the page can read it, so it is not secure storage. The app never uses localStorage, cookies or
  files for the key, and the backend never stores or logs it.
- **Cost:** answers are paid from the key's credit. "Test connection" may incur a small charge. There is no default model.
- **Instructors:** issue separate limited-credit keys per student or group (a credit limit and an expiry on each, in the
  OpenRouter dashboard or with its management API). Never share one unrestricted key.
- **Separate from your coding assistant:** this key and model are unrelated to Claude Code's or Cline's model or provider
  settings, and the app does not read or change those.

## Troubleshooting

| What you see | What to do |
|---|---|
| "port is in use" | Something else holds it; the launcher never stops it. Set `FRONTEND_PORT` and `BACKEND_PORT`. |
| "Live SEC data is not configured" | Add `SEC_USER_AGENT` to the root `.env` as above, then restart. It needs a name and an email. |
| "SEC refused the request (403)" | Check your contact line. The app does not retry; try later. |
| "SEC is limiting requests" | Wait the time shown. On shared networks, use Demo. |
| "No annual 10-K revenue…" | The filer has no annual 10-K revenue in a currency, for example a foreign filer using form 20-F. |
| Python not found or too old | Install Python 3.10 to 3.13, or set `APP_PYTHON` to its full path in the root `.env`. |
