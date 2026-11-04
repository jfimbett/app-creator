#!/usr/bin/env python3
"""Write the m2-01 record and checkpoint notes after the m2 tag exists. Run from the worktree root."""
import json
import re

SHA = "4451d43fd52f6e08c2db7a41b16434c4f078605e"
d = "runs/m2/m2-01-implement-main-session"
log = "/Users/[REDACTED:user]/Documents/app-creator/.logs/verify-4451d43-20261104T071359Z.log"
lines = open(log).read().split("\n")
keep = [lines[0], "... (full log kept locally in .logs/ of the main checkout, git-ignored)"]
keep += [l for l in lines if re.search(r"\d+ passed in|Test Files|^\s+Tests |^\s+\d+ passed", l)] + lines[-14:]
text = re.sub(r"/Users/[^/ ]+", "/Users/[REDACTED:user]", "\n".join(keep))
open(f"{d}/verify-clean-worktree.log", "w").write(text + "\n")

open(f"{d}/RESPONSE.md", "w").write("""# RESPONSE — m2-01-implement-main-session

[UNCAPTURED TOP-LEVEL MESSAGE] This step ran in the top-level session, not through scripts/dispatch-step.mjs. Its final
message is emitted after this file is committed, so it is not recorded here and must not be reconstructed. The running
updates between tool calls are likewise only in the session transcript. See RESULT.json, verify-clean-worktree.log,
live-evidence.log and review-checks.log for the observed results.
""")

result = {
    "stepId": "m2-01-implement-main-session", "milestone": "m2", "role": "top-level session (owner role)",
    "status": "completed", "startingCommit": "9ddd60d", "checkpointCommit": SHA, "date": "2026-11-04",
    "workspace": "isolated worktree .worktrees/m2, branch work/m2; removed after integration",
    "gateDecidedBy": "top-level session against the brief's section 9 gate; project-orchestrator not invoked, per the instruction to stay in the main session",
    "offlineGate": {
        "command": "bash scripts/verify-ref.sh 4451d43 (npm ci, npm run setup, npm run verify in a clean worktree with no .env)",
        "exit": 0,
        "summary": "toolkit ok; ruff ok; pytest 320 passed; frontend lint and typecheck ok; Vitest 83 passed; build ok; Playwright 24 passed",
    },
    "demoRun": "npm run demo on 3400/8400: data_mode fixtures, live_available false, source=live gives 409 live_disabled, statements load, no selector (2 journeys passed)",
    "liveSec": {
        "evidence": "live-evidence.log, fresh cache, 2026-11-04T07:14Z",
        "smoke": "live SEC: passed, 14 checks",
        "browserJourney": "e2e-live/live-sec.spec.ts passed: NVDA by ticker, Microsoft by name, Apple by CIK, statements, explorer, back to Demo; browser made no off-machine request",
        "crossCheck": "app values vs raw SEC JSON, no app code: NVIDIA, Apple, JPMorgan, McDonald's, 0 mismatches",
        "awkwardFilers": "TSMC 20-F explained; McDonald's n/m (negative equity); JPMorgan unavailable lines; unknown CIK 404",
        "secFailuresLive": "not provoked against real SEC; 403, 429, 503, timeout and redirects are tested with a mocked SEC only",
    },
    "visualInspection": ["live NVIDIA 1440", "Apple page 1440", "explorer 1440", "income 1366", "Apple page 390", "income 390 (after fix)", "ratios 390 (after fix)", "explorer 390"],
    "defectsFoundOnLiveData": ["debt 0 and D/E 0.00× from a lone short-term zero (NVIDIA FY2019)", "FCF from FY2012 shown as a key figure", "capex under an unmapped concept", "500 for a 20-F filer"],
    "testsChangedFromM1": ["test_api_m1: key figures now a superset; DATA_MODE=live became valid", "e2e/m1-foundation: restatement note uses .first() because the note now appears twice", "e2e/demo-journey: Net income toggle scoped to the chart"],
    "reviewType": "same-session read-only checks (m2_review.sh), not independent; independent reviewers not dispatched, per the instruction",
    "transcriptGaps": ["top-level final message not in RESPONSE.md (marker there)", "no dispatched steps in M2, so no per-step subagent responses exist", "patch scripts in this folder record exact edits; interim tool output is only in the session transcript"],
    "notRun": ["independent reviews", "Windows", "Cline", "GitHub CI (nothing pushed)", "the owner's own look"],
}
with open(f"{d}/RESULT.json", "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
    f.write("\n")

with open("runs/INDEX.md", "a") as f:
    f.write("\n## M2\n\n- 2026-11-04 · **m2/m2-01-implement-main-session** · top-level session · completed · [prompt](m2/m2-01-implement-main-session/PROMPT.md) · [response marker](m2/m2-01-implement-main-session/RESPONSE.md) · [result](m2/m2-01-implement-main-session/RESULT.json)\n")

s = open("PROGRESS.md").read()
s = re.sub(r"M1 complete at tag `m1`\. Execution mode[^\n]*",
           "M2 complete at tag `m2`. Execution mode (instructor, 2026-11-04): one milestone at a time, main session, then stop and report. **Waiting for the instructor; do not start M3 without instruction.**", s, count=1)
row = re.search(r"^\| `milestone/01-foundation` / `m1`.*$", s, re.M).group(0)
s = s.replace(row, row + f"\n| `milestone/02-financial-intelligence` / `m2` (annotated) | {SHA} | clean worktree npm ci → setup → verify exit 0 (2026-11-04 07:14Z): pytest 320, Vitest 83, Playwright 24; live SEC checks passed separately; gate decided in the main session; same-session review only |")
s = s.replace("`npm run dev` refuses them by design; use BACKEND_PORT/FRONTEND_PORT.", "`npm run dev` refuses them by design; use BACKEND_PORT/FRONTEND_PORT.")
s += """
## M2 completion (2026-11-04)

- Instruction saved before work in `runs/m2/m2-01-implement-main-session/PROMPT.md` and in `milestones/02-financial-intelligence/FOLLOWUPS.md`.
- **SEC contact:** at the owner's request, a root `.env` holds their `SEC_USER_AGENT` (git-ignored, permissions 600, created once by the assistant; value not recorded). `AGENTS.md` says assistants never create `.env`: this was the owner's explicit exception.
- Live testing on real companies found four defects that fixtures could not show; all fixed with tests (see `milestones/plan.md`).
- Deviations: synchronous SEC client (brief's table says async), capex alternate outside `CAPTURE_CONCEPTS`, stricter debt rule. Recorded in the architecture decision log.
- Classroom app: `FRONTEND_PORT=3200 BACKEND_PORT=8200 npm run dev` → http://127.0.0.1:3200 (starts on Demo, Live selector available). Plain offline demo: `npm run demo`.
- **Deferred:** M3–M5, independent reviews, GitHub publication, commit-email decision, permission hardening, remaining final documents. Next, only on instruction: M3 from `m2`.
"""
open("PROGRESS.md", "w").write(s)
print("ok")
