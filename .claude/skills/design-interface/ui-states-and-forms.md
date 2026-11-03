# UI states and forms

Every screen that loads data has more than one state. Design each one; never leave a blank area, a spinner
forever, or a raw error.

## 1. The states

| State | When | What the user sees | Example text |
|---|---|---|---|
| **Loading** | a request is in progress | a short message or skeleton rows in the place of the content; existing content stays visible when refreshing | "Loading weekly totals…" |
| **Empty** | the request worked, there is nothing yet | why it is empty and what to do next, with the action | "No runs recorded for week 12. **Add a run**" |
| **Error** | the request failed | plain message from the error envelope, a next step, a **Try again** button | "Could not reach the server. Is the backend running? **Try again**" |
| **Offline / demo** | the app runs on recorded or sample data (`npm run demo`) or the source is unreachable | a persistent, visible label with the data's date | "Demo data recorded 2026-03-01 — not live" |
| **Missing data** | some values are absent inside otherwise good data | "n/a" with the reason, in place, never 0 | "n/a (no runs last week)" |
| **Stale / cached** | data comes from a cache | its age and source | "Updated 3 h ago (cached)" |
| **Not configured** | an optional feature lacks a setting | the feature says so; the rest works | "Summaries are not set up." |
| **Success** | an action finished | a short confirmation near the action, focus where the user continues | "Run saved." |

Model the states explicitly so none is forgotten (the scaffold's `lib/health.ts` does this):

```ts
// <frontend>/lib/load-state.ts
export type LoadState<T> =
  | { kind: "loading" }
  | { kind: "ok"; data: T }
  | { kind: "empty" }
  | { kind: "error"; message: string; code: string };

export function toLoadState<T>(r: { ok: true; data: T } | { ok: false; error: { code: string; message: string } },
                               isEmpty: (d: T) => boolean): LoadState<T> {
  if (!r.ok) return { kind: "error", message: r.error.message, code: r.error.code };
  return isEmpty(r.data) ? { kind: "empty" } : { kind: "ok", data: r.data };
}
```

This is pure logic: test it with Vitest (ok, empty, error envelope, network failure).

Render each state in one shared component so wording and styling are consistent:

```tsx
// <frontend>/components/ui/StateMessage.tsx
import type { ReactNode } from "react";

export function StateMessage({ kind, children, action }: { kind: "loading" | "empty" | "error"; children: ReactNode; action?: ReactNode }) {
  return (
    <div role={kind === "error" ? "alert" : "status"} aria-live="polite" data-state={kind}
         className={`rounded-md border-l-4 px-3 py-2 ${kind === "error" ? "border-error" : "border-border text-muted"}`}>
      {kind === "error" && <span className="font-semibold">Error: </span>}
      {children}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
```

Rules:

- Show loading only after about 300 ms if you can, to avoid flicker; always within a second.
- `data-state` attributes (as in the scaffold) let Playwright wait for a state instead of sleeping.
- Errors never show stack traces, keys, file paths or internal ids (`plan-architecture`,
  [errors-and-validation.md](../plan-architecture/errors-and-validation.md)).
- Do not silently substitute other data when a request fails (for example demo data in place of a failed live
  search). Show the error; offer the alternative as an explicit choice.

## 2. Forms

Checklist for every form:

- [ ] Every input has a visible `<label htmlFor>` (placeholder text is not a label).
- [ ] Required fields are marked in text ("required"), not only with an asterisk or colour.
- [ ] The right input type: `type="number"` with `min`/`max`/`step`, `type="date"`, `inputMode="decimal"` on phones.
- [ ] Sensible defaults (today's date, the last used item).
- [ ] Client-side checks only to help typing; the server validates everything and its field errors are shown.
- [ ] Error messages say what is wrong **and how to fix it**, next to the field, linked with
      `aria-describedby`, and the field gets `aria-invalid="true"`.
- [ ] On submit with errors: a summary at the top ("2 fields need fixing") and focus moves to the first wrong field.
- [ ] The submit button shows progress ("Saving…") and is disabled while saving, to prevent double submits.
- [ ] After success: a confirmation, and the form either clears or shows the saved result.
- [ ] Typed input is kept when an error occurs.

```tsx
<div>
  <label htmlFor="distance" className="block text-sm font-medium">Distance (km), required</label>
  <input id="distance" name="distance_km" type="number" min="0.1" max="300" step="0.1" inputMode="decimal"
         aria-invalid={errors.distance_km ? "true" : undefined}
         aria-describedby={errors.distance_km ? "distance-error" : "distance-hint"}
         className="mt-1 w-full rounded-md border border-border bg-surface px-2 py-1.5 tabular-nums" />
  <p id="distance-hint" className="text-xs text-muted">Between 0.1 and 300 km.</p>
  {errors.distance_km && <p id="distance-error" className="text-sm text-error">Error: {errors.distance_km}</p>}
</div>
```

Map the server's `422` envelope (`details.fields[].field`, `.message`) to `errors` by field name.

Message wording:

| Weak | Better |
|---|---|
| "Invalid input" | "Distance must be between 0.1 and 300 km." |
| "Error 422" | "End date must be on or after the start date." |
| "Something went wrong" | "Could not save the run: the server is not responding. Your entry is kept; try again." |

## 3. Tests for states and forms

- Vitest: each state function (ok/empty/error/network) and the field-error mapping.
- Playwright (in `<frontend>/e2e/`, run by `npm run verify`): the main journey in the normal state, and at least
  one error or empty state (for example by calling a test-only fixture mode or by stopping a mocked route with
  `page.route("/api/...", r => r.fulfill({ status: 503, json: {...} }))`). Wait on `data-state`, never on a fixed
  delay.
