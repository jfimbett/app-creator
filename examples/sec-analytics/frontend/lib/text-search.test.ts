import { describe, expect, it } from "vitest";

import { countLabel, findMatches, highlightSegments, matchesByBlock, MAX_MATCHES, stepMatch } from "./text-search";

const blocks = [
  { id: 0, text: "Revenue grew. REVENUE fell." },
  { id: 1, text: "No hit here" },
  { id: 2, text: "Total revenue (net) cost $1.5 a.b axb" },
];

describe("findMatches (M3-AC5)", () => {
  it("is case-insensitive and in document order", () => {
    const { matches, capped } = findMatches(blocks, "revenue");
    expect(matches.map((m) => [m.blockId, m.start])).toEqual([[0, 0], [0, 14], [2, 6]]);
    expect(capped).toBe(false);
  });

  it("needs 2 characters and ignores surrounding spaces", () => {
    expect(findMatches(blocks, "r").matches).toEqual([]);
    expect(findMatches(blocks, " ").matches).toEqual([]);
    expect(findMatches(blocks, "  grew ").matches).toHaveLength(1);
  });

  it.each(["(net)", "$1.5", "a.b"])("treats %s literally, not as a pattern", (query) => {
    expect(findMatches(blocks, query).matches).toHaveLength(1);
  });

  it("does not throw on an invalid pattern", () => {
    expect(findMatches(blocks, "((").matches).toEqual([]);
    expect(findMatches(blocks, "\\").matches).toEqual([]);
    expect(findMatches(blocks, "[a-").matches).toEqual([]);
  });

  it("caps at 1,000 and says so", () => {
    const many = [{ id: 0, text: "ab ".repeat(MAX_MATCHES + 5) }];
    const result = findMatches(many, "ab");
    expect(result.matches).toHaveLength(MAX_MATCHES);
    expect(result.capped).toBe(true);
    expect(countLabel(result, 2)).toBe("3 of 1,000+");
  });
});

describe("count and steps", () => {
  it("counts from one", () => {
    expect(countLabel(findMatches(blocks, "revenue"), 0)).toBe("1 of 3");
    expect(countLabel(findMatches(blocks, "absent"), 0)).toBe("No matches");
  });

  it("wraps around at both ends", () => {
    expect(stepMatch(2, 1, 3)).toBe(0);
    expect(stepMatch(0, -1, 3)).toBe(2);
    expect(stepMatch(0, 1, 0)).toBe(0);
  });
});

describe("highlightSegments", () => {
  it("returns plain text when the block has no match", () => {
    expect(highlightSegments("abc", undefined)).toEqual([{ text: "abc", matchIndex: null }]);
  });

  it("numbers matches across blocks and joins back to the original", () => {
    const { matches } = findMatches(blocks, "revenue");
    const byBlock = matchesByBlock(matches);
    const first = highlightSegments(blocks[0].text, byBlock.get(0));
    expect(first.map((s) => s.matchIndex)).toEqual([0, null, 1, null]);
    expect(first.map((s) => s.text).join("")).toBe(blocks[0].text);
    const third = highlightSegments(blocks[2].text, byBlock.get(2));
    expect(third.filter((s) => s.matchIndex !== null)).toEqual([{ text: "revenue", matchIndex: 2 }]);
  });
});
