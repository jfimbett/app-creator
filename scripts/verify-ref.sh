#!/usr/bin/env bash
# Verify a git ref in an isolated, clean worktree (own node_modules, .venv, caches, no .env):
#   bash scripts/verify-ref.sh <ref> [log-dir]
# Creates .worktrees/verify-<ref>, runs npm ci → npm run setup → npm run verify, writes a log, then removes
# only the worktree it created. Never touches the main working tree or other worktrees.
set -u
ref="$1"
logdir="${2:-.logs}"
root="$(git rev-parse --show-toplevel)"
name="verify-$(echo "$ref" | tr '/:' '--')"
wt="$root/.worktrees/$name"
mkdir -p "$root/$logdir"
log="$root/$logdir/$name-$(date -u +%Y%m%dT%H%M%SZ).log"

if [ -e "$wt" ]; then echo "refusing: $wt already exists" >&2; exit 2; fi
git -C "$root" worktree add --detach "$wt" "$ref" >/dev/null || exit 2
sha="$(git -C "$wt" rev-parse HEAD)"
status=0
{
  echo "ref=$ref sha=$sha started=$(date -u +%FT%TZ) node=$(node --version)"
  echo "== npm ci";          (cd "$wt" && npm ci --no-audit --no-fund) || status=1
  [ $status -eq 0 ] && { echo "== npm run setup"; (cd "$wt" && npm run setup) || status=1; }
  [ $status -eq 0 ] && { echo "== npm run verify"; (cd "$wt" && npm run verify) || status=1; }
  echo "finished=$(date -u +%FT%TZ) exit=$status"
} >"$log" 2>&1
git -C "$root" worktree remove --force "$wt" >/dev/null 2>&1
echo "$ref $sha exit=$status log=$log"
exit $status
