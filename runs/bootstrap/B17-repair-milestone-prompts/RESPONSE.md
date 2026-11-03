# RESPONSE — B17-repair-milestone-prompts

- From: product-architect → to: owner (top-level Claude Code session)
- Captured by: scripts/dispatch-step.mjs from the `result` field of `claude -p --output-format json`
- Session id: c6f11ee6-5b2e-40fa-adab-b563e1527084 (local Claude Code transcript; not committed)
- Finished: 2026-11-03T18:12:49.253Z; exit code 0; status completed
- Redaction: only explicit [REDACTED:<kind>] markers were inserted; otherwise verbatim.

<!-- VERBATIM:BEGIN -->
I applied every edit B14 listed to the milestone prompts and the planning documents. The toolkit check passes and no email addresses appear in the edited files. I did not change M4's prompt, since B14 accepted it as it was.

**Prompt edits:**
- **M1:** the fixture test now looks for the marker `SYNTHETIC: invented for tests` or a `"_synthetic"` key, instead of the bare word `SYNTHETIC`.
- **M2:**
  - `FilingMeta` is removed from the shared shapes, with a note that it arrives in M3.
  - A `docs/SETUP.md` row for live SEC mode is added after the `examples/sec-analytics/README.md` row.
  - The optional `.invalid` User-Agent sentence is added to the `test_sec_client_m2.py` bullet.
- **M3:**
  - Section 11 now forbids editing only the existing fixture data files. It still allows adding new files, their manifest entries and the `fixtures/README.md` update.
  - The optional "enforced while the response is read" rule is added after the 20 MB limit.
- **M5:**
  - The origin check now refuses a request if **either** check fails (it said "and" before).
  - A `Sec-Fetch-Site: cross-site` test case is added.
  - A `docs/SETUP.md` row for the optional AI analyst is added.

**B13 open items 1, 2, 3, 4, 6, 7 and 9:**
- `milestones/acceptance.md`: M1-AC6 and V2 now include 1366 px; M2-AC5 now says stacked charts, one per metric; M4-AC6 now counts CSV data points.
- `milestones/architecture.md`: the screenshot widths, the new filing-document path, and the plain pydantic settings model.
- `milestones/plan.md`: the toolkit exception for slice 1.1; filing excerpts removed from slice 1.2; `capture_fixtures.py --filings` added to slice 3.2.
- `milestones/README.md` and `milestones/01-foundation/README.md`: the two stale sentences replaced.
- `docs/PRODUCT-DECISIONS.md`: six dated rows added under "Changes to earlier decisions" (items 1, 2, 3, 4, 6 and 7), each citing B14 as the basis.

Several quoted texts were split across lines in the files. I matched them across the line break and kept the wording exactly. In the plan's ground rules and in the M3 and M5 prompts, I re-wrapped the surrounding lines to fit.

**Prompt hashes after the edits (sha256):**
- M1 `527634f27e04bde1392334565b70e4f7e3fc5ad26f0505389c5928599193d338`
- M2 `35112cc9b79ee5304f42df528a26b585b9532e26c577dd25ef71813322fbc45b`
- M3 `a1b69395b5387acfb756aa9cf53dd7d7421278478cb73138867801e7cc4020f7`
- M4 `47af2b5062577555faebece9d10555599c84382852921c74b8267fb971740b32` (unchanged)
- M5 `c3caadf1aa1c028df547644284d1b1892c23c7bf797c7d220e2cb8253e198c99`

Two documents now disagree with the new decisions. I left both alone because neither was in B14's list:
- **M1 prompt, line 451:** its quote of M1-AC6 still says "at 1440 and 390 px (this prompt adds 1366 px)". The acceptance criterion now lists all three widths.
- **`milestones/product.md`, line 106:** it still describes filing documents as "excerpts … trimming recorded". Architecture and decisions now say whole documents, gzip-compressed and unmodified, captured in M3.

## Handoff
Changes: milestones/01-foundation/PROMPT.md, milestones/02-financial-intelligence/PROMPT.md, milestones/03-filing-intelligence/PROMPT.md, milestones/05-ai-financial-analyst/PROMPT.md, milestones/README.md, milestones/01-foundation/README.md, milestones/acceptance.md, milestones/architecture.md, milestones/plan.md, docs/PRODUCT-DECISIONS.md. runs/ not touched (its existing changes were already there).
Verification evidence: `npm run check-toolkit` exit 0 (34 ok, 3 warnings, 0 failures). Email grep over milestones/ and docs/PRODUCT-DECISIONS.md: no matches (exit 1). sha256 of the five prompts listed above. Checked that the M3 prompt's `fixtures/filings/<CIK10>/<accession>/<primaryDocument>.gz` path matches architecture.md.
Remaining findings: the M1 prompt's quote of M1-AC6 (line 451) and product.md line 106 (filing "excerpts") are stale; both are outside the B14 edit list, so the owner needs to decide on them. Item 5 needs no edit; items 8 and 10 (N1, N2) stay open as B14 recorded.
Next action: owner records the new hashes and dispatches the B14 re-check before creating `template-v1`, deciding first whether to fix the two stale lines.
<!-- VERBATIM:END -->
