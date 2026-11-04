# UNFINISHED: M3 Filing intelligence, work in progress

**This branch is not a verified release and has no `m3` tag.** The verified classroom version is `main` (M2 functionality), tag `m2`.
Work stopped on 2026-11-04 at the instructor's classroom freeze. Nothing here has been opened in a browser.

## What exists

- Backend: filing list and reader endpoints, archive address validation, HTML sanitizer, section detection, permanent document cache, bounded download.
- Recorded data: the latest 10-K and 10-Q of Apple, Microsoft and Alphabet, stored unmodified (gzip), and older submissions pages for Microsoft and Alphabet.
- Frontend: Filings tab, latest panel, history table, reader, section navigation, text search.

## What was checked

| Check | Result | Kind |
|---|---|---|
| `npm run verify` before any change | exit 0 | baseline of the starting commit, not of this code |
| `capture_fixtures.py --filings` | exit 0, 8 real SEC requests | real SEC data, by script |
| pytest | 431 passed | offline; recorded filings plus mocked SEC failures |
| ruff, eslint, TypeScript | no findings at the last run | static |
| `lib/text-search.test.ts` | 10 of 11 at the last run; fixed afterwards, **not re-run** | unit |

## What was NOT done

`npm run verify` on this code, the production build, the browser journey (`e2e/m3-filings.spec.ts` was not written), any look at the screens, the live journey through the app,
the full Vitest suite, documentation and `milestones/acceptance.md` statuses. Treat the screens as untested.

## To finish

Run `npm run setup` and `npm run verify`, write the browser journey, then look at the screens. Instructions: `runs/m3/m3-02-implement-main-session/PROMPT.md`.
