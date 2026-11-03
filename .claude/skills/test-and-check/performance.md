# Performance: measure first, then fix the slowest thing

Companion to [SKILL.md](SKILL.md). Rule: **no optimization without a measurement before and after.** Write both
numbers in the change report ("`GET /api/items`: 1.8 s → 120 ms, median of 5 calls, fixture data"). If you cannot
measure a problem, there is nothing to optimize yet.

## 1. Find out where the time goes

| Symptom | Measure with | Look for |
|---|---|---|
| A page feels slow | browser DevTools → Network (disable cache), Performance tab | one slow `/api` call, a huge JavaScript file, many sequential requests |
| One endpoint is slow | `curl -s -o /dev/null -w "%{time_total}\n" http://127.0.0.1:8000/api/items` (run 5 times) | which part: the database, an external API, a computation |
| Inside the backend | a timer log around suspects (below), or `python -m cProfile -s cumtime` on a script that calls the function | the function with the largest cumulative time |
| Large frontend bundle | `npm run build` output in `<frontend>` (route sizes and first-load JS) | a route much bigger than the others; a big library imported for one small use |
| Tests got slow | `pytest --durations=10`; `npx vitest run --reporter=verbose` | a test calling the network or sleeping for real |

A small timing log for the backend (remove or keep at debug level afterwards; never log secrets):

```python
import logging
import time
from contextlib import contextmanager

log = logging.getLogger("app.timing")


@contextmanager
def timed(label: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        log.info("%s took %.0f ms", label, (time.perf_counter() - start) * 1000)

# with timed("load items"): items = db.list_items(conn)
```

Measure with realistic data sizes (fixture mode, or a generated dataset of the size the product expects), on the
production build for the frontend (`npm run verify` builds it; `next dev` is always slower).

## 2. Common causes and fixes

**N+1 queries.** One query for a list, then one more query per row (100 rows → 101 queries). Recognise it by
counting queries in a test or log. Fix with one query that joins or uses `WHERE id IN (...)`:

```python
# slow: one query per item
for item in items:
    item["tags"] = conn.execute("SELECT name FROM tags WHERE item_id = ?", (item["id"],)).fetchall()

# fast: one query for all items (placeholders built from the count, values still passed as parameters)
ids = [item["id"] for item in items]
marks = ",".join("?" * len(ids))
rows = conn.execute(f"SELECT item_id, name FROM tags WHERE item_id IN ({marks})", ids).fetchall()
```

Also add an index for columns used in `WHERE` and `ORDER BY` on large tables (a migration, `manage-data`), and
check with `EXPLAIN QUERY PLAN`.

**External calls in the request path.** Cache them (disk cache with expiry, `integrate-api`), fetch independent
ones concurrently (`asyncio.gather`), and never call a provider once per row.

**Recomputing the same result.** Cache derived results in memory (`functools.lru_cache` for pure functions with
hashable arguments) or on disk with a version in the key.

**Sending too much data.** Paginate lists (`?limit=50&offset=0`), send only the fields the screen needs, and
aggregate on the server rather than shipping thousands of points to a chart (a chart with 10,000 points is also
unreadable; see `design-interface`).

**Large frontend bundle.** Import only what you use (`import { LineChart } from "recharts"`), load heavy,
rarely used components with `next/dynamic`, keep data fetching and big dependencies in server components where
possible, and do not add a library for one small helper.

**Blocking work in async endpoints.** In FastAPI, slow blocking code (big file parsing, `sqlite3`, CPU work)
inside `async def` blocks every other request. Use plain `def` endpoints for blocking code (FastAPI runs them in a
thread pool) or move long work to a background job (`manage-data`).

**Re-renders.** In React, fetch data once per page, not in every list item; memoize expensive derived values with
`useMemo` only after measuring with the React DevTools Profiler.

## 3. Keep it fixed

- Add a test that protects the fix where it is cheap: for N+1, assert the number of queries (wrap the connection
  or count `sqlite3` trace callbacks via `conn.set_trace_callback`); for pagination, assert the limit.
- Do not add timing assertions with tight thresholds to `npm run verify`: they flake on slower machines. A generous
  bound (for example "under 2 s with fixture data") is acceptable if it caught a real problem.
- Record the before/after numbers in `<docs>/plan.md` (progress log).

## Stop and ask

Before adding infrastructure for speed (a cache server, a CDN, a paid database tier, a queue): explain the
measurement and the cheaper options tried first. These cost money or add services, so the owner decides.
