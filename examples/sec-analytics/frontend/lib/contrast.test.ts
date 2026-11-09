import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { contrastRatio, NON_TEXT_ROLES, parseThemeTokens, SURFACE_ROLES, TEXT_ROLES } from "./contrast";

describe("contrastRatio (WCAG 2.x relative luminance)", () => {
  it("black on white is 21:1", () => {
    expect(contrastRatio("#000000", "#ffffff")).toBeCloseTo(21, 2);
  });

  it("#777777 on white is 4.48:1", () => {
    expect(Math.round(contrastRatio("#777777", "#ffffff") * 100) / 100).toBe(4.48);
  });

  it("does not depend on the order or on 3-digit shorthand", () => {
    expect(contrastRatio("#fff", "#000")).toBeCloseTo(21, 2);
    expect(contrastRatio("#ffffff", "#777777")).toBeCloseTo(contrastRatio("#777777", "#ffffff"), 6);
  });

  it("rejects colours it cannot measure", () => {
    expect(() => contrastRatio("var(--x)", "#ffffff")).toThrow();
  });
});

// Token values are read from globals.css itself, so the test checks what the app really ships.
const css = readFileSync(join(__dirname, "..", "app", "globals.css"), "utf8");
const themes = parseThemeTokens(css);

describe.each(["dark", "light"] as const)("%s theme tokens (M6-AC1, O1)", (theme) => {
  const tokens = themes[theme];

  it("defines every checked role as a hex colour", () => {
    for (const role of [...TEXT_ROLES, ...NON_TEXT_ROLES, ...SURFACE_ROLES, "on-accent"]) {
      expect(tokens[role], `${theme} --${role}`).toMatch(/^#[0-9a-f]{6}$/i);
    }
  });

  for (const role of TEXT_ROLES) {
    for (const surface of SURFACE_ROLES) {
      it(`--${role} on --${surface} is at least 4.5:1`, () => {
        expect(contrastRatio(tokens[role], tokens[surface])).toBeGreaterThanOrEqual(4.5);
      });
    }
  }

  for (const role of NON_TEXT_ROLES) {
    for (const surface of ["bg", "panel"] as const) {
      it(`--${role} on --${surface} is at least 3:1`, () => {
        expect(contrastRatio(tokens[role], tokens[surface])).toBeGreaterThanOrEqual(3);
      });
    }
  }

  it("--on-accent on --accent is at least 4.5:1", () => {
    expect(contrastRatio(tokens["on-accent"], tokens.accent)).toBeGreaterThanOrEqual(4.5);
  });
});
