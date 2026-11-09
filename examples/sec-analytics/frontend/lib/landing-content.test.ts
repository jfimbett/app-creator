import { describe, expect, it } from "vitest";

import {
  ABOUT,
  ABOUT_LABEL,
  DISCLAIMER,
  FAQ,
  FEATURES,
  HOW_IT_WORKS,
  LANDING_NAV,
  PRICING_NOTE,
  PRICING_TIERS,
  REVIEWS_LABEL,
  TESTIMONIALS,
} from "./landing-content";

// Real, well-known firms that must never appear as a fictional reviewer's organisation (O3, brief §6).
const REAL_FIRMS = [
  "goldman",
  "morgan stanley",
  "jpmorgan",
  "j.p. morgan",
  "blackrock",
  "vanguard",
  "fidelity",
  "citadel",
  "bloomberg",
  "deloitte",
  "pwc",
  "kpmg",
  "ernst",
  "mckinsey",
  "harvard",
  "stanford",
  "wharton",
  "mit ",
  "apple",
  "microsoft",
  "google",
  "alphabet",
  "sec.gov",
  "securities and exchange commission",
];

// Invented popularity claims the brief forbids (O3): aggregate ratings, user counts.
const INVENTED_STATS = /\b\d[\d,.]*\s*(\+\s*)?(users|analysts|students|reviews|ratings|customers|downloads)\b|\b\d(\.\d)?\s*(\/\s*5|stars?\b)/i;

const allText = JSON.stringify({ FEATURES, HOW_IT_WORKS, TESTIMONIALS, PRICING_TIERS, ABOUT, FAQ });

describe("landing page content (M6-AC4, O3–O5)", () => {
  it("labels the testimonials, the prices and the company as fictional or illustrative", () => {
    expect(REVIEWS_LABEL).toBe("Fictional testimonials written for this teaching demo.");
    expect(PRICING_NOTE).toBe("Prices are illustrative. This teaching app has no accounts and takes no payments.");
    expect(ABOUT_LABEL).toBe("SEC Analytics and its team are fictional, created for a programming course.");
  });

  it("states the SEC disclaimer", () => {
    expect(DISCLAIMER).toContain("not affiliated with or endorsed by the U.S. Securities and Exchange Commission");
    expect(DISCLAIMER).toContain("public SEC EDGAR");
    expect(DISCLAIMER).toContain("not investment advice");
  });

  it("has six features and three steps", () => {
    expect(FEATURES).toHaveLength(6);
    expect(HOW_IT_WORKS).toHaveLength(3);
  });

  it("has 4 to 6 testimonials with initials avatars and no real organisation", () => {
    expect(TESTIMONIALS.length).toBeGreaterThanOrEqual(4);
    expect(TESTIMONIALS.length).toBeLessThanOrEqual(6);
    for (const t of TESTIMONIALS) {
      expect(t.initials).toMatch(/^[A-Z]{2}$/);
      const org = `${t.role} ${t.organisation ?? ""}`.toLowerCase();
      for (const firm of REAL_FIRMS) expect(org, `${t.name}: ${firm}`).not.toContain(firm);
      if (t.stars !== undefined) expect(t.stars).toBeGreaterThanOrEqual(1);
      if (t.stars !== undefined) expect(t.stars).toBeLessThanOrEqual(5);
    }
  });

  it("makes no invented popularity claims anywhere", () => {
    expect(allText).not.toMatch(INVENTED_STATS);
    for (const banned of ["AI-verified", "real-time", "real time", "bank-grade", "official"]) {
      expect(allText.toLowerCase()).not.toContain(banned.toLowerCase());
    }
  });

  it("sends every pricing button to /app or an in-page anchor, with exactly one highlighted tier", () => {
    expect(PRICING_TIERS).toHaveLength(3);
    for (const tier of PRICING_TIERS) expect(tier.cta.href).toMatch(/^(\/app|#[a-z-]+)$/);
    expect(PRICING_TIERS.filter((tier) => tier.highlighted)).toHaveLength(1);
    expect(PRICING_TIERS[1].highlighted).toBe(true);
  });

  it("uses only example.com contact addresses (RFC 2606)", () => {
    const emails = allText.match(/[\w.+-]+@[\w.-]+/g) ?? [];
    expect(emails.length).toBeGreaterThan(0);
    for (const email of emails) expect(email).toMatch(/@example\.com$/);
    expect(ABOUT.contact).toBe("hello@example.com");
  });

  it("has 3 to 4 fictional team members with initials", () => {
    expect(ABOUT.team.length).toBeGreaterThanOrEqual(3);
    expect(ABOUT.team.length).toBeLessThanOrEqual(4);
    for (const person of ABOUT.team) expect(person.initials).toMatch(/^[A-Z]{2}$/);
  });

  it("answers the five FAQ questions of the brief", () => {
    const questions = FAQ.map((item) => item.question.toLowerCase()).join(" | ");
    for (const topic of ["data come from", "investment advice", "key", "affiliated", "store"]) expect(questions).toContain(topic);
  });

  it("links the header to the five sections", () => {
    expect(LANDING_NAV.map((item) => item.href)).toEqual(["#features", "#reviews", "#pricing", "#about", "#faq"]);
  });
});
