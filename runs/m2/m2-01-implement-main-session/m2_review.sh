#!/usr/bin/env bash
# Same-session read-only review of the M2 diff (not independent). Run from the worktree root.
E=examples/sec-analytics
echo "== fixtures and briefs unchanged since m1 (expect no lines)"
git diff --stat m1 HEAD -- $E/fixtures milestones/02-financial-intelligence/PROMPT.md milestones/03-filing-intelligence/PROMPT.md GOAL.md .claude/settings.json | cut -c1-90
echo "== toolkit files changed since m1 (expect none)"
git diff --name-only m1 HEAD -- .claude scripts scaffold AGENTS.md CLAUDE.md docs/TOOLKIT.md | cut -c1-90
echo "== browser code fetching SEC, raw HTML, browser storage, public env (expect none)"
grep -rnE "fetch\([^)]*sec\.gov|dangerouslySetInnerHTML|localStorage|sessionStorage|NEXT_PUBLIC" $E/frontend/app $E/frontend/components $E/frontend/lib | cut -c1-120
echo "== SEC calls outside the client (expect none)"
grep -rnE "httpx\.(get|post|Client|AsyncClient)|requests\." $E/backend/app --include=*.py | grep -v 'clients/sec.py' | cut -c1-110
echo "== endpoints taking a caller URL (expect none)"
grep -rnE "url: *(str|Annotated)|Query\(.*url" $E/backend/app/api | cut -c1-110
echo "== user agent printed or logged (expect none)"
grep -rnE "(print|logger\.[a-z]+|log)\(.*(agent|USER_AGENT)" $E/backend/app $E/backend/scripts | cut -c1-110
echo "== later-milestone or valuation features in the UI (expect none)"
grep -rniE ">[^<]*(filings|compare|analyst|openrouter|market cap|P/E|coming soon)" $E/frontend/app $E/frontend/components | cut -c1-110
grep -rnE "href=[^ ]*(filings|compare|analyst)" $E/frontend/app $E/frontend/components | cut -c1-110
echo "== tracked secrets, contact, env or cache (expect none)"
git grep -nIE 'sk-or-v1-[A-Za-z0-9]|sk-ant-[A-Za-z0-9]|gh[pousr]_[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}|@gmail\.com' -- . ':!scripts/dispatch-step.mjs' ':!runs/bootstrap/B15b-review-toolkit-security/RESPONSE.md' | cut -c1-100
git ls-files | grep -E '(^|/)\.env$|\.cache/|node_modules/' | head -3
echo "== missing values turned into 0 in logic (expect none)"
grep -nE " or 0\b|\.get\([^)]*, *0\)" $E/backend/app/logic/*.py | cut -c1-100
echo "== ancestry"; git merge-base --is-ancestor m1 HEAD && echo "m1 is an ancestor"; git rev-parse m1^{commit} | cut -c1-7
