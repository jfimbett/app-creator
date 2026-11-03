# Caching and background jobs

Most course apps need neither. Add one only when an acceptance criterion needs it, and choose the simplest option
that meets it.

## Do you need a cache?

| Symptom | Cache? |
|---|---|
| An external source is slow (> 1 s) or rate-limited, and its data changes rarely | yes: disk cache with a time-to-live (TTL) |
| The offline demo must work without network | not a cache: **recorded fixtures**, labelled as such (`integrate-api`) |
| A calculation over local data is slow | first measure; usually fix the query or the algorithm |
| Data must always be current (a balance, a stock level) | no, or a very short TTL shown to the user |

## Options, simplest first

1. **No cache.** Fetch when asked. Fine for fast sources and low traffic.
2. **In-memory, per process**: `functools.lru_cache` for pure, small lookups. Lost on restart; never for
   per-user data.
3. **Disk cache with TTL** (recommended when caching is needed): one JSON file per request key in a git-ignored
   folder, with the time it was fetched.
4. **SQLite table** as cache, when you also need to query cached rows. See `manage-data`.
5. A cache server (Redis): not for the MVP.

```python
# <backend>/app/data/cache.py
import hashlib, json, time
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parents[2] / ".cache" / "http"   # git-ignored

def cached(key: str, ttl_s: int, fetch) -> tuple[object, float, bool]:
    """Returns (data, fetched_at_epoch, from_cache)."""
    path = CACHE_DIR / (hashlib.sha256(key.encode()).hexdigest() + ".json")
    if path.exists():
        entry = json.loads(path.read_text())
        if time.time() - entry["fetched_at"] < ttl_s:
            return entry["data"], entry["fetched_at"], True
    data = fetch()                       # may raise: do not cache failures
    now = time.time()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"fetched_at": now, "data": data}))
    tmp.replace(path)                    # atomic: no half-written files
    return data, now, False
```

Rules:

- **Never cache errors or empty responses caused by an error.**
- **The user sees the data's age**: return `fetched_at` and a `source` (`live`, `cache`, `fixture`) with the data,
  and show "Updated 3 hours ago (cached)". Old data must never look current.
- The cache key includes everything that changes the answer (URL, parameters, user if any), never a secret.
- When the source fails and a stale entry exists, decide (and record) whether to show it **labelled as stale**
  or to show the error. Never silently.
- Tests: use a temporary directory (`tmp_path`) for `CACHE_DIR`, a fake `fetch`, and a fake clock; check hit,
  miss, expiry and "failure not cached".
- Add the cache folder to `.gitignore` and say in the README how to clear it (delete the folder).

## Do you need a background job?

| Need | Simplest option |
|---|---|
| Work after a request that the user need not wait for (send an email) | FastAPI `BackgroundTasks` |
| A task that takes 10–60 s (an import) | run it in a `BackgroundTasks`, store its status, let the UI poll `GET /api/imports/<id>` |
| Something every day/hour (refresh data) | a script run by hand or by the host's scheduler at deployment time (`prepare-deploy`); not inside the dev server |
| Many long tasks, retries, several workers | a job queue: not for the MVP; record it as a later decision |

```python
from fastapi import BackgroundTasks

@app.post("/api/imports", status_code=202)
def start_import(body: ImportIn, tasks: BackgroundTasks) -> ImportStatus:
    job = create_job(body)                    # status "queued", stored in SQLite or a file
    tasks.add_task(run_import, job.id)        # runs after the response is sent
    return job
```

Rules for jobs:

- Status is stored (`queued`, `running`, `done`, `failed` with a message) so the UI can show progress and errors.
- A job can be run again safely (idempotent): re-importing the same file does not duplicate rows.
- `BackgroundTasks` stop when the server stops; that is acceptable for a course demo, and must be written down.
- Tests call the job function directly; they do not wait for background threads.
