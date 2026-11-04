// Text search inside a loaded filing (brief §3, M3-AC5). Pure functions, so the rules are easy to test:
// literal text, not a pattern; case-insensitive; from 2 characters; at most 1,000 highlighted matches.

export const MIN_QUERY_LENGTH = 2;
export const MAX_MATCHES = 1000;

export interface SearchableBlock {
  id: number;
  text: string;
}

/** One match: `start` and `end` are character positions inside the block's text. */
export interface TextMatch {
  blockId: number;
  start: number;
  end: number;
}

export interface SearchResult {
  matches: TextMatch[];
  /** True when more matches exist than the 1,000 that are highlighted. */
  capped: boolean;
}

export interface TextSegment {
  text: string;
  /** Position in the whole match list, or null for plain text between matches. */
  matchIndex: number | null;
}

const NO_RESULT: SearchResult = { matches: [], capped: false };

function literalPattern(query: string): RegExp {
  return new RegExp(query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "giu");
}

export function normalizeQuery(query: string): string {
  return query.trim();
}

/** All matches in document order, up to the limit. Too short a query finds nothing. */
export function findMatches(blocks: readonly SearchableBlock[], rawQuery: string): SearchResult {
  const query = normalizeQuery(rawQuery);
  if (query.length < MIN_QUERY_LENGTH) return NO_RESULT;
  const pattern = literalPattern(query);
  const matches: TextMatch[] = [];
  for (const block of blocks) {
    pattern.lastIndex = 0;
    for (const found of block.text.matchAll(pattern)) {
      if (matches.length === MAX_MATCHES) return { matches, capped: true };
      matches.push({ blockId: block.id, start: found.index, end: found.index + found[0].length });
    }
  }
  return { matches, capped: false };
}

/** The text of "3 of 41". */
export function countLabel(result: SearchResult, current: number): string {
  if (result.matches.length === 0) return "No matches";
  const total = result.capped ? `${MAX_MATCHES.toLocaleString("en-US")}+` : String(result.matches.length);
  return `${current + 1} of ${total}`;
}

/** The next match position, wrapping around at both ends. */
export function stepMatch(current: number, step: 1 | -1, total: number): number {
  if (total === 0) return 0;
  return (current + step + total) % total;
}

export interface BlockMatches {
  /** Index of this block's first match in the whole list. */
  firstIndex: number;
  ranges: { start: number; end: number }[];
}

/** Groups the match list by block, for fast rendering. */
export function matchesByBlock(matches: readonly TextMatch[]): Map<number, BlockMatches> {
  const byBlock = new Map<number, BlockMatches>();
  matches.forEach((match, index) => {
    const entry = byBlock.get(match.blockId);
    if (entry) entry.ranges.push({ start: match.start, end: match.end });
    else byBlock.set(match.blockId, { firstIndex: index, ranges: [{ start: match.start, end: match.end }] });
  });
  return byBlock;
}

/** Splits a block's text into plain and highlighted pieces. Joined back, they are the original text. */
export function highlightSegments(text: string, entry: BlockMatches | undefined): TextSegment[] {
  if (!entry) return [{ text, matchIndex: null }];
  const segments: TextSegment[] = [];
  let position = 0;
  entry.ranges.forEach((range, offset) => {
    if (range.start > position) segments.push({ text: text.slice(position, range.start), matchIndex: null });
    segments.push({ text: text.slice(range.start, range.end), matchIndex: entry.firstIndex + offset });
    position = range.end;
  });
  if (position < text.length) segments.push({ text: text.slice(position), matchIndex: null });
  return segments;
}
