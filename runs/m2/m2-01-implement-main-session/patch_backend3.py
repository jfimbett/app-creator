#!/usr/bin/env python3
"""Wrap long docstring lines and restore a constant used by M1 tests. Run from the backend folder."""


def sub(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        assert old in s, (path, old[:60])
        s = s.replace(old, new, 1)
    open(path, "w").write(s)


sub("app/clients/sec.py", [
    ("""Used by the running app in live mode (through `data/source.py`), by `scripts/capture_fixtures.py`
and by `scripts/live_sec_smoke.py`. Thread-safe: FastAPI runs the sync endpoints in a thread pool, and
this client lets one request out at a time. Single flight and the disk cache are in `data/`.
""", """Used by the running app in live mode (through `data/source.py`), by
`scripts/capture_fixtures.py` and by `scripts/live_sec_smoke.py`. Thread-safe: FastAPI runs the
sync endpoints in a thread pool, and this client lets one request out at a time. Single flight and
the disk cache are in `data/`.
"""),
    ("""    def __init__(self, message: str, retry_after: float, upstream_status: int | None = None) -> None:
""", """    def __init__(
        self, message: str, retry_after: float, upstream_status: int | None = None
    ) -> None:
"""),
])
sub("app/data/cache.py", [
    ("""File: `<root>/<sha256 of the URL>.json` holding `{url, retrieved_at, status, body}`. Files are written
atomically (temporary file, then rename). A corrupt or foreign file is ignored and refetched, and an
expired entry is treated as absent. There is no background refresh.
""", """File: `<root>/<sha256 of the URL>.json` holding `{url, retrieved_at, status, body}`. Files are
written atomically (temporary file, then rename). A corrupt or foreign file is ignored and
refetched, and an expired entry is treated as absent. There is no background refresh.
"""),
])
sub("app/data/source.py", [
    ('''"""Where each request's data comes from: recorded fixtures, the disk cache or SEC, and how it is labelled.
''', '''"""Where each request's data comes from (fixtures, disk cache or SEC) and how it is labelled.
'''),
])
sub("app/logic/concepts.py", [
    ("""- Interest expense: Apple has `InterestExpense` to FY2023 and nothing after it; Microsoft and Alphabet
  move to `InterestExpenseNonoperating`. `InterestExpenseDebt` (Apple to FY2021) is a narrower last resort.
""", """- Interest expense: Apple has `InterestExpense` to FY2023 and nothing after it; Microsoft and
  Alphabet move to `InterestExpenseNonoperating`. `InterestExpenseDebt` (Apple to FY2021) is a
  narrower last resort.
"""),
])
sub("app/logic/metrics.py", [
    ("""Every result keeps its formula and inputs. When a number would be wrong or misleading it is not computed:
""", """Every result keeps its formula and inputs. When a number would be wrong or misleading it is not
computed:
"""),
    ("""- `not_meaningful`: the arithmetic works but does not measure what the label says (negative equity, or
  growth from a prior value at or below zero). Shown as n/m with a reason, never as a number.
""", """- `not_meaningful`: the arithmetic works but does not measure what the label says (negative
  equity, or growth from a prior value at or below zero). Shown as n/m with a reason, never as a
  number.
"""),
    ("""Negative equity: with equity below zero, ROE and debt-to-equity do not measure return or leverage in the
usual way, so they are not shown as numbers; the tooltip lists the raw inputs.
""", """Negative equity: with equity below zero, ROE and debt-to-equity do not measure return or leverage
in the usual way, so they are not shown as numbers; the tooltip lists the raw inputs.
"""),
    ('''"""Sum of the debt components reported at that date; none reported means unavailable, never 0."""''',
     '''"""Sum of the debt components reported at that date; none means unavailable, never 0."""'''),
    ("""    With no beginning balance, the ending balance is used and labelled. An average below zero is n/m.
""", """    With no beginning balance, the ending balance is used and labelled. An average below zero is
    n/m.
"""),
])
sub("app/logic/statements.py", [
    ("""These are labelled summaries built from SEC Company Facts, not reproductions of filed statements. Pure logic
over one Company Facts document (no files, network or clock). The selection policy is in `logic/periods.py`.
""", """These are labelled summaries built from SEC Company Facts, not reproductions of filed statements.
Pure logic over one Company Facts document (no files, network or clock). The selection policy is
in `logic/periods.py`.
"""),
    ('''RESTATEMENT_NOTE = "Values may''', '''NET_INCOME_MISSING_REASON = f"no {NET_INCOME_CONCEPT} fact"
RESTATEMENT_NOTE = "Values may'''),
])
print("ok")
