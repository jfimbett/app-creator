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

## Follow-up 2 (2026-11-09, after the M6 report): no sound in the video; hydration error on the running site

Typed by the instructor in the top-level session after the M6 report, before pushing. Appended here after it was acted
on (the fix was small and made in the same turn); the tag `m6` was left where it was.

```text
i cant here anything in the video, also the website has t his error
[pasted: a Next.js "Hydration failed" overlay; the server rendered the old CompanySearch markup]
stop the serve ryourself and start again the correct one
```

- **Website:** the instructor's running server (launched from the main checkout before the merge) served build output
  from its stale `.next` cache. The session stopped that launcher and its children, deleted
  `examples/sec-analytics/frontend/.next` (build cache) and started `npm run demo` again. Checked: 6 screens × 2 themes in
  a browser, no console or hydration errors. No code change was needed.
- **Video sound:** the audio track was present (−15.7 LUFS) but half its energy was below 200 Hz, which laptop speakers
  barely play. The music was remixed (pad an octave up, louder pluck and bells, a kick with a second harmonic, high-pass at
  70 Hz) and re-muxed at −14 LUFS target (measured −13.5 LUFS, true peak −1.5 dBFS); the picture is unchanged. Also noted:
  VS Code's built-in player cannot decode AAC audio, so the file plays silently there.

## Follow-up 3 (2026-11-09): no voice in the video; stop the server

Typed by the instructor after the remix. Appended here after it was acted on (stopping a server changes no files).

```text
there is subtitles but no voice its pretty, bad stop the server
```

- The session stopped the `npm run demo` it had started (and the launcher's child processes, which outlived the stop).
- The video was made without narration: the brief forbade installing anything in the autonomous run, and brag-slim has
  no voice. The session offered three choices: the full /brag with a downloaded voice model, the robotic built-in Windows
  voice, or keeping the video. **The instructor chose "Keep it as is"**, so the video stays music and captions only.

## Follow-up 4 (2026-11-09): commit and push M6

Recorded in [runs/m6/m6-02-publish-main-session/PROMPT.md](../../runs/m6/m6-02-publish-main-session/PROMPT.md)
before the documentation changes and the push.

```text
ok commit and push m6, and make sure all branches are properly explained, witht heir prompts recorded etc. just like we did with m1 and m2
```
