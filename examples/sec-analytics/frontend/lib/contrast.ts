// WCAG 2.x contrast ratio, used by the token test to check both themes (M6-AC1).
// Formula: https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio and #dfn-relative-luminance

/** Roles drawn as text: each must reach 4.5:1 on every surface. */
export const TEXT_ROLES = ["text", "text-muted", "accent", "link", "positive", "negative", "warning"] as const;
/** Surfaces text sits on. */
export const SURFACE_ROLES = ["bg", "panel", "panel-raised"] as const;
/** Non-text UI that must be seen (control borders, focus ring, chart series): 3:1 on bg and panel. */
export const NON_TEXT_ROLES = [
  "border-strong",
  "focus",
  "series-revenue",
  "series-net-income",
  "series-1",
  "series-2",
  "series-3",
  "series-4",
] as const;

function channel(value: number): number {
  const c = value / 255;
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

function parseHex(colour: string): [number, number, number] {
  const match = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(colour.trim());
  if (!match) throw new Error(`Not a hex colour: ${colour}`);
  let hex = match[1];
  if (hex.length === 3) hex = hex.replace(/./g, (c) => c + c);
  return [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16)) as [number, number, number];
}

export function relativeLuminance(colour: string): number {
  const [r, g, b] = parseHex(colour).map(channel);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** (lighter + 0.05) / (darker + 0.05), from 1 to 21. */
export function contrastRatio(a: string, b: string): number {
  const [la, lb] = [relativeLuminance(a), relativeLuminance(b)];
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
}

/**
 * Reads the custom properties of `:root { … }` (dark) and `:root[data-theme="light"] { … }` (light) from
 * globals.css. Light inherits every dark value it does not override, as in the browser. A value that is
 * `var(--other)` is resolved to the other token's value.
 */
export function parseThemeTokens(css: string): Record<"dark" | "light", Record<string, string>> {
  const block = (selector: RegExp) => {
    const match = selector.exec(css);
    if (!match) throw new Error(`Block not found: ${selector}`);
    const out: Record<string, string> = {};
    for (const [, name, value] of match[1].matchAll(/--([\w-]+)\s*:\s*([^;]+);/g)) out[name] = value.trim();
    return out;
  };
  const resolve = (tokens: Record<string, string>) => {
    const out: Record<string, string> = {};
    for (const name of Object.keys(tokens)) {
      let value = tokens[name];
      for (let i = 0; i < 5; i += 1) {
        const ref = /^var\(--([\w-]+)\)$/.exec(value);
        if (!ref || tokens[ref[1]] === undefined) break;
        value = tokens[ref[1]];
      }
      out[name] = value;
    }
    return out;
  };
  const dark = block(/:root\s*\{([^}]*)\}/);
  const light = { ...dark, ...block(/:root\[data-theme="light"\]\s*\{([^}]*)\}/) };
  return { dark: resolve(dark), light: resolve(light) };
}
