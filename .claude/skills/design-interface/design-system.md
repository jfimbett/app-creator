# Design system: tokens, themes, type, spacing

A design system here is a short list of named values (tokens) and a few components that every screen reuses,
so the app looks consistent without anyone deciding colours or spacing per page. Keep it in one place:
`<frontend>/app/globals.css` (tokens) and `<frontend>/components/ui/` (shared components).

## 1. Colour tokens as CSS variables (Tailwind CSS v4)

Name colours by **role**, not by hue (`--surface`, not `--gray-900`). The scaffold already defines
`--background`, `--surface`, `--foreground`, `--muted`, `--border`, `--ok`, `--error`, `--focus`, with dark as
the default and a light theme from the system setting. Extend it; do not start a second palette.

```css
/* <frontend>/app/globals.css */
@import "tailwindcss";

:root {                      /* dark is the default */
  color-scheme: dark;
  --background: #0f1115;
  --surface: #171a21;
  --surface-raised: #1e222b;
  --foreground: #e8eaed;
  --muted: #a8adb7;
  --border: #2e333d;
  --accent: #60a5fa;         /* one accent colour for primary actions and the main series */
  --accent-foreground: #0b1220;
  --ok: #4ade80;
  --warn: #fbbf24;
  --error: #f87171;
  --focus: #93c5fd;
}

@media (prefers-color-scheme: light) {
  :root:not([data-theme="dark"]) { color-scheme: light; --background: #ffffff; --surface: #f6f7f9;
    --surface-raised: #ffffff; --foreground: #16181d; --muted: #4b5260; --border: #d5d9e0;
    --accent: #1d4ed8; --accent-foreground: #ffffff; --ok: #166534; --warn: #92400e; --error: #b91c1c; --focus: #1d4ed8; }
}
:root[data-theme="light"] { /* repeat the light values above here, for a manual theme toggle */ }

/* Make the tokens available as Tailwind utilities: bg-surface, text-muted, border-border, ring-focus ... */
@theme inline {
  --color-background: var(--background);
  --color-surface: var(--surface);
  --color-surface-raised: var(--surface-raised);
  --color-foreground: var(--foreground);
  --color-muted: var(--muted);
  --color-border: var(--border);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-ok: var(--ok);
  --color-warn: var(--warn);
  --color-error: var(--error);
  --color-focus: var(--focus);
}

/* Optional manual toggle: lets `dark:` utilities follow data-theme as well as the system setting */
@custom-variant dark (&:where([data-theme="dark"], [data-theme="dark"] *));
```

Then components write `bg-surface text-foreground border-border`, never raw hex values. (The scaffold's own
components use the longer `bg-[var(--surface)]` form, which works too; prefer the named utilities in new code.)

Rules:

- **Contrast**: body text on its background at least 4.5:1, large text and UI borders that carry meaning 3:1,
  in **both** themes. Check each new pair (see [responsive-and-accessibility.md](responsive-and-accessibility.md)).
- **Status colours** (`ok`, `warn`, `error`) always come with a word or symbol ("Error:", "▲ +2.0").
- **Chart series**: the accent first, then at most 3–4 more distinguishable colours defined as tokens
  (`--series-2` …); check them in both themes.
- Dark mode first if the product asks for it; light mode must still be readable (no black text on dark surfaces
  left over).

## 2. Typography scale

Use few sizes and weights. Suggested scale (Tailwind defaults):

| Role | Class | Use |
|---|---|---|
| Page title | `text-2xl font-semibold` | one `<h1>` per page |
| Section | `text-lg font-semibold` | `<h2>` |
| Body | `text-base` (16 px) | paragraphs, forms |
| Dense data | `text-sm` (14 px) | tables, secondary labels |
| Caption | `text-xs text-muted` (12 px) | units, sources, timestamps; never smaller |
| Key number | `text-3xl font-semibold tabular-nums` | the headline value on a card |

- One font family for text (the system stack in the scaffold, or one font loaded with `next/font`), a monospace
  for code and ids. Loading fonts from a third-party CDN at runtime is a decision for the owner.
- Numbers in tables and cards: `tabular-nums` so digits line up.
- Line length for text: about 60–80 characters (`max-w-prose`).

## 3. Spacing and density

- Use Tailwind's 4 px steps and a few of them consistently: `gap-2` (8 px) inside controls, `gap-4` (16 px)
  between related items, `gap-6`/`gap-8` between sections. Page padding `px-4` on phones, `px-6` or more on
  laptops.
- **Density** is a product decision (`product.md`, "Density"):
  - *comfortable*: `py-3` table rows, `text-base`, more white space — forms and occasional users;
  - *compact*: `py-1.5` rows, `text-sm`, tighter gaps — data-heavy tools for frequent users. Keep touch targets
    at least 24×24 px (44×44 px preferred on phones) even when compact.
- Group with space and one border or background change, not boxes inside boxes. Avoid decorative card grids
  that do not help the journey.

## 4. Components (shadcn/ui style)

shadcn/ui is not a package you install as a dependency: its CLI copies the source of each component into your
project (`components/ui/`), built on Radix primitives and styled with Tailwind and CSS variables. You own and can
edit the code.

- Use it when a component is hard to get accessible by hand: dialog, dropdown menu, popover, tabs, combobox,
  tooltip, toast. Plain elements (button, input, table) can stay simple hand-written components.
- Adding it downloads code and packages, so check the current shadcn/ui documentation for the Next.js and Tailwind
  v4 setup and ask before running its CLI (for example `npx shadcn@latest init`, then `npx shadcn@latest add
  dialog`). Commit the generated files and the lockfile; record the decision.
- Map its variables (`--primary`, `--card`, `--ring`, …) to your role tokens instead of keeping two palettes.
- Make your own small shared components for repeated patterns: `Button`, `Card`, `StatCard`, `DataTable`,
  `StateMessage` (loading/empty/error, see [ui-states-and-forms.md](ui-states-and-forms.md)).

```tsx
// <frontend>/components/ui/Button.tsx
import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" };

export function Button({ variant = "secondary", className = "", ...props }: Props) {
  const look = variant === "primary"
    ? "bg-accent text-accent-foreground hover:opacity-90"
    : "border border-border hover:bg-surface-raised";
  return (
    <button
      {...props}
      className={`rounded-md px-3 py-1.5 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2
        focus-visible:outline-focus disabled:opacity-50 ${look} ${className}`}
    />
  );
}
```

## 5. Checklist for a new screen

- [ ] Only role tokens (no hex values in components).
- [ ] Sizes from the type scale; numbers `tabular-nums`.
- [ ] Spacing from the few chosen steps; density matches `product.md`.
- [ ] Shared components reused (no second button style).
- [ ] Looked at in dark and light at 390 and 1366 px.
