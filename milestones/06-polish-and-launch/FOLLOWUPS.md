# M6 Polish and launch: follow-up prompts and corrections

This file records every follow-up prompt or correction that changes this milestone's implementation after
[PROMPT.md](PROMPT.md) was dispatched. Each one is appended here **before it is acted on**, with its date, sender and
the step record in `runs/` that it belongs to. Entries are never edited or removed afterwards. PROMPT.md stays
unchanged.

## Follow-up 1 (2026-11-09): start M6

Typed by the instructor in the top-level session after `/clear`. Recorded in
[runs/m6/m6-01-implement-main-session/PROMPT.md](../../runs/m6/m6-01-implement-main-session/PROMPT.md) before any
implementation work. It started the milestone with the brief unchanged.

```text
Run milestones/06-polish-and-launch/PROMPT.md, starting at its section 0. Work autonomously and report at the end.
```

## Correction 1 (2026-11-09, slice 6.2): the M5 localStorage assertions (brief §4.5)

Not a new instruction: the brief itself asks for this change and for its record here.

- **Was:** `e2e/m5-analyst.spec.ts` asserted `Object.keys(localStorage)` is `[]` in three places (M5-AC2).
- **Now:** a helper `expectLocalStorageSafe(page)` asserts that the only allowed key is `sec-analytics.theme`, that
  its value is `"dark"` or `"light"`, and that no key or value contains the test key `test-key-not-real-0000` or any
  part of it of four or more characters. The settings test now switches the theme first, so localStorage really
  holds the theme entry while the key is typed, saved, remembered and forgotten.
- **Why:** the theme preference (owner decision O1) is the app's first localStorage entry. The security property of
  M5-AC2 is "the AI key never reaches localStorage", not "localStorage is empty". `lib/ai-key.test.ts` (no
  `localStorage.setItem` from the key holder) is unchanged.
