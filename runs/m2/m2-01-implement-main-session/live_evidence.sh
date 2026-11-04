#!/usr/bin/env bash
# Final live SEC evidence on the M2 candidate. Run from the worktree root with `npm run dev` on 3300/8300.
# Prints each check's outcome and never the contact. Output is saved next to this script by the caller.
ROOT="$(pwd)"
BASE=http://127.0.0.1:3300
rm -rf examples/sec-analytics/backend/.cache/sec
echo "== date: $(date -u +%FT%TZ); commit: $(git rev-parse --short HEAD)"
echo "== 1. live smoke script (3 requests through the app's client)"
(cd examples/sec-analytics/backend && .venv/bin/python scripts/live_sec_smoke.py); echo "exit=$?"
echo "== 2. live browser journey (NVDA by ticker, Apple by CIK, Microsoft by name; empty cache)"
(cd examples/sec-analytics/frontend && BASE_URL=$BASE PLAYWRIGHT_BROWSERS_PATH="$ROOT/.cache/ms-playwright" \
  npx --no-install playwright test --config playwright.live.config.ts 2>&1 | grep -E '✓|✘|^ +[0-9]+ (passed|failed)|Error:'); echo "exit=${PIPESTATUS[0]}"
echo "== 3. app values vs raw SEC JSON, no app code (NVIDIA, Apple, JPMorgan, McDonald's)"
python3 runs/m2/m2-01-implement-main-session/live_crosscheck.py $BASE 0001045810 0000320193 0000019617 0000063908; echo "exit=$?"
echo "== 4. awkward filers through the API"
curl -s -m 60 "$BASE/api/companies/0001046179/financials?source=live" | python3 -c "import json,sys;d=json.load(sys.stdin);print('TSMC (20-F):',d['source']['label'],'| periods',len(d['periods']),'|',d['notes'])"
curl -s -m 60 "$BASE/api/companies/0000063908/financials?source=live" | python3 -c "
import json,sys;d=json.load(sys.stdin);r={l['metric_id']:l['values'][-1] for l in d['ratios']}
print('McDonald\'s negative equity: D/E',r['debt_to_equity']['status'],'|',r['debt_to_equity']['reason'],'| ROE',r['roe']['reason'])"
curl -s -m 60 "$BASE/api/companies/search?q=9999999999&source=live" | python3 -c "import json,sys;d=json.load(sys.stdin);print('CIK not in ticker file:',d['results'][0]['name'],'|',d['source']['mode'])"
curl -s -m 60 -o /dev/null -w 'unknown CIK at SEC: HTTP %{http_code}\n' "$BASE/api/companies/9999999999?source=live"
