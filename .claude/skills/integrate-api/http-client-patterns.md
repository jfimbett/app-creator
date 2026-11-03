# HTTP client patterns (FastAPI + httpx)

Practical companion to [SKILL.md](SKILL.md). The code below is a complete, small example: a reusable client,
a FastAPI route that uses it, and pytest tests with `respx` (HTTP mocking). It was run with the scaffold's pinned
versions (FastAPI 0.150, httpx 0.28, respx 0.23, pytest 9.1): 8 tests passed and `ruff check` was clean with the
scaffold's `pyproject.toml`. Copy the parts you need into `<backend>/app/clients/` and `<backend>/tests/`, then
adapt the base URL, allowlist and limits to the provider's documentation.

## Checklist for every integration

| Concern | Rule | Where in the code |
|---|---|---|
| Who calls | the backend only; the browser calls `/api/*` | route in `main.py` |
| Where to | fixed base URL + path allowlist (regular expressions matched in full) | `_check` |
| Redirects | followed only if the target passes the same allowlist; at most 3 | `_fetch` |
| Identification | `User-Agent` with app name and a project URL (from settings) when the provider asks | `ApiClient(user_agent=...)` |
| Timeouts | 5 s connect, 10 s overall per request | `httpx.Timeout(10.0, connect=5.0)` |
| Throttling | stay under the documented limit, shared by all requests of the process | `_throttle` |
| Retries | GET only; timeouts, 429, 5xx; max 3 attempts; backoff 1 s, 2 s, 4 s + jitter; `Retry-After` wins (capped 60 s) | `_fetch`, `_delay` |
| No retries | 400, 401, 403, 404, bad JSON | `_fetch` |
| De-duplication | identical concurrent requests share one in-flight call | `_inflight` |
| Cache | one JSON file per request key, written atomically, expiry per client | `_read_cache`, `_write_cache` |
| Provenance | `source` (URL without query), `retrieved_at` (UTC), `mode` (`live`/`cached`/`fixture`) | `Fetched` |
| Errors | one exception type per failure; routes turn them into friendly 404/502/503 | exceptions, route |
| Secrets | keys from settings, sent in a header; never in logs, `source`, cache files or error text | your adapter |

## The client: `<backend>/app/clients/http.py`

```python
"""Safe outgoing HTTP for one provider.

Allowlist, timeouts, throttling, retries with backoff, de-duplication, disk cache, provenance.
"""

import asyncio
import hashlib
import json
import os
import random
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx


class UpstreamError(Exception):
    """Base class: the provider could not give us usable data."""


class NotAllowed(UpstreamError):
    """The URL (or a redirect target) is outside the allowlist."""


class NotFound(UpstreamError):
    pass


class BadCredentials(UpstreamError):
    pass


class RateLimited(UpstreamError):
    pass


class Unavailable(UpstreamError):
    pass


class BadData(UpstreamError):
    pass


@dataclass(frozen=True)
class Fetched:
    data: object
    source: str  # URL without query string (queries can carry keys)
    retrieved_at: str  # ISO 8601, UTC
    mode: str  # "live" | "cached" | "fixture"


class ApiClient:
    def __init__(
        self,
        base_url: str,
        allowed_paths: list[str],
        *,
        user_agent: str,
        per_second: float | None = 5.0,
        cache_dir: Path | None = None,
        ttl_seconds: float = 24 * 3600,
        max_attempts: int = 3,
        transport: httpx.AsyncBaseTransport | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._base = httpx.URL(base_url)
        self._allowed = [re.compile(p) for p in allowed_paths]
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"User-Agent": user_agent},
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=False,  # we follow them ourselves, after checking the target
            transport=transport,
        )
        self._interval = 1.0 / per_second if per_second else 0.0
        self._next_slot = 0.0
        self._lock = asyncio.Lock()
        self._inflight: dict[str, asyncio.Task[Fetched]] = {}
        self._cache_dir, self._ttl, self._max_attempts, self._sleep = (
            cache_dir, ttl_seconds, max_attempts, sleep)

    async def aclose(self) -> None:
        await self._client.aclose()

    # -- public -----------------------------------------------------------------------------
    async def get_json(self, path: str, params: dict[str, str] | None = None) -> Fetched:
        self._check(self._base.join(path))
        key = hashlib.sha256(f"{path}?{sorted((params or {}).items())}".encode()).hexdigest()
        if (cached := self._read_cache(key)) is not None:
            return cached
        if key in self._inflight:  # same request already running: share its result
            return await self._inflight[key]
        task = asyncio.ensure_future(self._fetch(path, params, key))
        self._inflight[key] = task
        try:
            return await task
        finally:
            self._inflight.pop(key, None)

    # -- internals --------------------------------------------------------------------------
    def _check(self, url: httpx.URL) -> None:
        if url.scheme != self._base.scheme or url.host != self._base.host:
            raise NotAllowed(f"host not allowed: {url.host}")
        if not any(p.fullmatch(url.path) for p in self._allowed):
            raise NotAllowed(f"path not allowed: {url.path}")

    async def _throttle(self) -> None:
        if not self._interval:
            return
        async with self._lock:
            now = time.monotonic()
            wait = self._next_slot - now
            self._next_slot = max(now, self._next_slot) + self._interval
        if wait > 0:
            await self._sleep(wait)

    @staticmethod
    def _delay(attempt: int, retry_after: str | None) -> float:
        if retry_after:
            try:
                return min(float(retry_after), 60.0)
            except ValueError:
                try:
                    when = parsedate_to_datetime(retry_after)
                    return max(0.0, min((when - datetime.now(timezone.utc)).total_seconds(), 60.0))
                except (TypeError, ValueError):
                    pass
        return min(2 ** (attempt - 1), 30) + random.uniform(0, 0.5)  # 1 s, 2 s, 4 s ... plus jitter

    async def _fetch(self, path: str, params: dict[str, str] | None, key: str) -> Fetched:
        url: httpx.URL = self._base.join(path)
        redirects = 0
        attempt = 0
        while True:
            attempt += 1
            await self._throttle()
            try:
                r = await self._client.get(url, params=params)
            except httpx.TransportError as error:  # includes timeouts and refused connections
                if attempt >= self._max_attempts:
                    raise Unavailable(type(error).__name__) from None
                await self._sleep(self._delay(attempt, None))
                continue
            if r.is_redirect and r.next_request is not None:
                redirects += 1
                if redirects > 3:
                    raise Unavailable("too many redirects")
                url, params = r.next_request.url, None
                self._check(url)  # a redirect must stay on the allowlist
                attempt -= 1
                continue
            if r.status_code == 404:
                raise NotFound(url.path)
            if r.status_code in (401, 403):
                raise BadCredentials(f"HTTP {r.status_code}")
            if r.status_code == 429 or r.status_code >= 500:
                if attempt >= self._max_attempts:
                    kind = RateLimited if r.status_code == 429 else Unavailable
                    raise kind(f"HTTP {r.status_code}")
                await self._sleep(self._delay(attempt, r.headers.get("Retry-After")))
                continue
            if r.status_code >= 400:
                raise UpstreamError(f"HTTP {r.status_code}")
            try:
                data = r.json()
            except ValueError:
                raise BadData("response is not JSON") from None
            fetched = Fetched(
                data=data,
                source=str(r.url.copy_with(query=None)),
                retrieved_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                mode="live",
            )
            self._write_cache(key, fetched)
            return fetched

    def _read_cache(self, key: str) -> Fetched | None:
        if not self._cache_dir:
            return None
        file = self._cache_dir / f"{key}.json"
        try:
            entry = json.loads(file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None  # missing or damaged entry: fetch again
        if time.time() - entry["stored_at"] > self._ttl:
            return None
        return Fetched(entry["data"], entry["source"], entry["retrieved_at"], "cached")

    def _write_cache(self, key: str, fetched: Fetched) -> None:
        if not self._cache_dir:
            return
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        tmp = self._cache_dir / f"{key}.json.tmp"
        tmp.write_text(json.dumps({**asdict(fetched), "stored_at": time.time()}), encoding="utf-8")
        os.replace(tmp, self._cache_dir / f"{key}.json")  # atomic: readers never see half a file
```

Notes:

- **Keys.** If the provider needs a key, add it as a header in `headers=` when creating the client, from your
  settings object. Prefer a header to a query parameter: query strings end up in logs. `source` drops the query
  anyway.
- **One client per provider, created once** (in the FastAPI lifespan below), so throttling, connection reuse and
  de-duplication work across requests. With several worker processes, each has its own throttle; divide the limit
  by the number of workers, or keep one worker for a small app.
- **Cache keys** must include everything that changes the answer (path and parameters, and the user if answers are
  per user). Never put a user's key in the cache key or the file.

## Using it in a route: `<backend>/app/main.py`

```python
from contextlib import asynccontextmanager
from pathlib import Path as FsPath

from fastapi import FastAPI, HTTPException, Path, Request

from app.clients.http import ApiClient, NotFound, RateLimited, Unavailable, UpstreamError

SERIES_ID = r"^[A-Z0-9_]{1,32}$"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.stats = ApiClient(
        "https://api.example.org",  # in a real app: from config (settings), not hard-coded
        allowed_paths=[r"/v1/series/[A-Z0-9_]{1,32}"],
        user_agent="ExampleApp/0.1 (+https://example.org/about)",
        cache_dir=FsPath(".cache/http/stats"),
        ttl_seconds=24 * 3600,
    )
    yield
    await app.state.stats.aclose()


app = FastAPI(lifespan=lifespan)


@app.get("/api/series/{series_id}")
async def series(request: Request, series_id: str = Path(pattern=SERIES_ID)) -> dict:
    try:
        got = await request.app.state.stats.get_json(f"/v1/series/{series_id}")
    except NotFound:
        raise HTTPException(404, "No series with that id.") from None
    except (Unavailable, RateLimited):
        raise HTTPException(503, "The statistics service is not answering. Try again.") from None
    except UpstreamError:
        raise HTTPException(502, "The statistics service sent data we could not read.") from None
    # Provenance travels with the values so the page can say where and when they came from.
    return {"values": got.data, "source": got.source,
            "retrieved_at": got.retrieved_at, "mode": got.mode}
```

The path pattern on `series_id` rejects bad input (422) before any outgoing call, and the allowlist in the client
is a second line of defense. In a real app the base URL, contact URL and cache folder come from settings, and
`.cache/` is git-ignored.

## Tests with respx: `<backend>/tests/test_http_client.py`

`respx` replaces httpx's network layer: a request to a mocked route gets the response you define, and a request
to anything not mocked fails, so a test can never reach the internet by accident. The fake `sleep` records waits
instead of waiting, which keeps tests fast and lets them assert on `Retry-After`.

```python
import asyncio

import httpx
import pytest
import respx

from app.clients.http import ApiClient, NotAllowed, NotFound

BASE = "https://api.example.org"


def make_client(tmp_path, sleeps):
    async def fake_sleep(seconds: float) -> None:  # records waits instead of waiting
        sleeps.append(seconds)

    return ApiClient(BASE, [r"/v1/series/[A-Z0-9_]{1,32}"], user_agent="ExampleApp/0.1 (test)",
                     per_second=None, cache_dir=tmp_path, sleep=fake_sleep)


@respx.mock
def test_429_waits_for_retry_after_then_succeeds(tmp_path):
    route = respx.get(f"{BASE}/v1/series/POP").mock(side_effect=[
        httpx.Response(429, headers={"Retry-After": "2"}),
        httpx.Response(200, json={"2025": 100}),
    ])
    sleeps: list[float] = []
    got = asyncio.run(make_client(tmp_path, sleeps).get_json("/v1/series/POP"))
    assert got.data == {"2025": 100} and got.mode == "live"
    assert sleeps == [2.0] and route.call_count == 2


@respx.mock
def test_404_is_not_retried(tmp_path):
    route = respx.get(f"{BASE}/v1/series/NOPE").mock(return_value=httpx.Response(404))
    with pytest.raises(NotFound):
        asyncio.run(make_client(tmp_path, []).get_json("/v1/series/NOPE"))
    assert route.call_count == 1


def test_path_outside_allowlist_is_refused_without_a_request(tmp_path):
    with respx.mock(assert_all_called=False) as mock:
        with pytest.raises(NotAllowed):
            asyncio.run(make_client(tmp_path, []).get_json("/admin/users"))
        assert not mock.calls


@respx.mock
def test_redirect_to_another_host_is_refused(tmp_path):
    respx.get(f"{BASE}/v1/series/POP").mock(
        return_value=httpx.Response(302, headers={"Location": "https://evil.example.net/x"}))
    with pytest.raises(NotAllowed):
        asyncio.run(make_client(tmp_path, []).get_json("/v1/series/POP"))


@respx.mock
def test_second_call_comes_from_cache(tmp_path):
    route = respx.get(f"{BASE}/v1/series/POP").mock(return_value=httpx.Response(200, json=[1, 2]))
    client = make_client(tmp_path, [])
    asyncio.run(client.get_json("/v1/series/POP"))
    again = asyncio.run(client.get_json("/v1/series/POP"))
    assert again.mode == "cached" and route.call_count == 1


@respx.mock
def test_concurrent_identical_requests_share_one_call(tmp_path):
    route = respx.get(f"{BASE}/v1/series/POP").mock(return_value=httpx.Response(200, json=[1]))
    client = ApiClient(BASE, [r"/v1/series/[A-Z0-9_]{1,32}"], user_agent="t", per_second=None)

    async def both():
        path = "/v1/series/POP"
        return await asyncio.gather(client.get_json(path), client.get_json(path))

    asyncio.run(both())
    assert route.call_count == 1
```

And the route, through FastAPI's `TestClient` (`<backend>/tests/test_series_route.py`). `pass_through()` lets the
test client's own requests through respx; replacing `_sleep` skips the real backoff waits:

```python
import httpx
import respx
from fastapi.testclient import TestClient

from app.main import app


@respx.mock
def test_provider_down_gives_a_friendly_503(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # the disk cache goes to a temporary folder
    respx.get("https://api.example.org/v1/series/POP").mock(side_effect=httpx.ConnectTimeout("slow"))
    respx.route(host="testserver").pass_through()
    with TestClient(app) as client:
        client.app.state.stats._sleep = _no_wait
        response = client.get("/api/series/POP")
    assert response.status_code == 503
    assert "Try again" in response.json()["detail"]


def test_bad_id_is_rejected_before_any_call():
    with TestClient(app) as client:
        assert client.get("/api/series/pop;rm").status_code == 422


async def _no_wait(_seconds: float) -> None:
    return None
```

The scaffold's `requirements.lock` already pins `httpx` and `respx`, and `npm run verify` runs these tests with
`pytest -q`.

## Fixture mode (offline demo and verify)

Keep recorded and synthetic data apart, and say which is which:

```text
<backend>/fixtures/
  recorded/
    stats_series_POP.json        # a real response, trimmed; no keys, tokens or personal data
    stats_series_POP.meta.json   # {"source": "https://api.example.org/v1/series/POP", "retrieved_at": "2026-11-03T09:00:00Z",
                                 #  "trimmed": "kept years 2015-2025", "kind": "recorded"}
  synthetic/
    stats_series_GAP.json        # {"_synthetic": true, "note": "2020 missing on purpose", ...}
```

- A setting such as `DATA_MODE=live|fixtures` (default `fixtures` if no key is set) picks the source. Put
  `"demoEnv": {"DATA_MODE": "fixtures"}` in `app-creator.config.json` so `npm run demo` and the verify browser
  test run offline.
- In fixture mode, return `Fetched(..., mode="fixture")` with `source` and `retrieved_at` from the `.meta.json`
  file, so the page says "recorded sample from 3 Nov 2026", not "live".
- Synthetic fixtures are for tests of edge cases. Never show them in the demo as if they were real data.
- Re-record a fixture by hand, with a small documented script, when the provider's format changes. Check the diff
  for secrets before committing.

## Optional: an AI / LLM provider call

The same client pattern applies (allowlisted base URL, timeouts, no retry on 4xx). Differences:

```python
from fastapi import Header, HTTPException

MAX_INPUT_CHARS = 8_000
MAX_OUTPUT_TOKENS = 600


@app.post("/api/explain")
async def explain(body: ExplainRequest, x_user_api_key: str | None = Header(default=None)) -> dict:
    if len(body.text) > MAX_INPUT_CHARS:
        raise HTTPException(413, f"Please shorten the text to {MAX_INPUT_CHARS} characters.")
    key = x_user_api_key or settings.llm_api_key  # user key for this request only, or a server setting
    if not key:
        raise HTTPException(400, "Add an API key in Settings to use explanations.")
    try:
        answer = await llm.complete(body.text, api_key=key, max_tokens=MAX_OUTPUT_TOKENS)
    except UpstreamError:
        raise HTTPException(503, "The AI service is not answering. Try again.") from None
    return {"answer": answer, "label": "AI-generated; check before relying on it"}
```

- The user key arrives in a header, is passed to one call, and is never assigned to anything that outlives the
  request (no global, no cache, no log line, no exception message). Starlette does not log request headers by
  default; do not add middleware that does.
- `ExplainRequest`, `settings` and `llm` stand for your own Pydantic model, settings object and provider client;
  check the provider's documentation for its endpoint, model names and limits.
- Add a per-session rate limit (for example 10 requests per minute) before exposing it beyond your laptop.
- Tests mock the provider with `respx` and assert that the key appears in the outgoing header and nowhere in the
  response or captured logs (`caplog`).

## Debugging an integration

1. Reproduce with the test client and `respx` first; only then try one live call by hand.
2. Log the method, path (no query), status, duration and attempt number; never headers or bodies with secrets.
3. A sudden 403 often means a missing or rejected `User-Agent` or key; a 429 means slow down (check the throttle);
   a redirect refusal means the provider moved the endpoint (update the allowlist after reading its docs).
