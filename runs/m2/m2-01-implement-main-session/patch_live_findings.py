#!/usr/bin/env python3
"""Fixes for defects found by looking at live NVIDIA data. Tests first. Run from the example folder.

Phase "tests" adds the failing tests; phase "code" applies the fixes.
"""
import sys


def sub(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        assert old in s, (path, old[:70])
        s = s.replace(old, new, 1)
    open(path, "w").write(s)


if sys.argv[1] == "tests":
    open("backend/tests/test_metrics_edges.py", "a").write('''

def test_debt_without_any_long_term_component_is_unavailable_not_zero() -> None:
    """Found on live data: a reported short-term 0 must not read as "this company has no debt"."""
    result = metrics.debt(
        [
            mv("debt_long_term_noncurrent", None),
            mv("debt_long_term_current", None),
            mv("debt_short_term", 0),
        ]
    )
    assert_unavailable(result, "no long-term debt concept reported")
    assert_unavailable(
        metrics.debt_to_equity(result, mv("equity", 100)), "no long-term debt concept reported"
    )
''')
    sub("backend/tests/test_metrics_edges.py", [
        ('''    result = metrics.debt([mv("a", 0), mv("b", None), mv("c", None)])
    assert (result.status, result.value) == ("ok", 0)
''', '''    result = metrics.debt(
        [
            mv("debt_long_term_noncurrent", 0),
            mv("debt_long_term_current", None),
            mv("debt_short_term", None),
        ]
    )
    assert (result.status, result.value) == ("ok", 0)
'''),
        ('''    result = metrics.debt([mv("a", None), mv("b", None), mv("c", None)])
''', '''    result = metrics.debt(
        [
            mv("debt_long_term_noncurrent", None),
            mv("debt_long_term_current", None),
            mv("debt_short_term", None),
        ]
    )
'''),
    ])
    open("backend/tests/test_periods_m2.py", "a").write('''

def test_capex_uses_the_alternate_concept_when_the_first_is_absent() -> None:
    """Found on live data: NVIDIA tags capex as PaymentsToAcquireProductiveAssets."""
    result = build_financials(
        doc(
            Revenues=[fact(*FY25, 100)],
            NetCashProvidedByUsedInOperatingActivities=[fact(*FY25, 40)],
            PaymentsToAcquireProductiveAssets=[fact(*FY25, 15)],
        ),
        URL,
    )
    capex = result.series["capex"][0]
    assert (capex.value, capex.provenance.concept) == (15, "PaymentsToAcquireProductiveAssets")
    assert result.series["fcf"][0].value == 25


def test_ppe_capex_wins_when_both_concepts_exist_and_they_are_never_summed() -> None:
    result = build_financials(
        doc(
            Revenues=[fact(*FY25, 100)],
            PaymentsToAcquirePropertyPlantAndEquipment=[fact(*FY25, 10)],
            PaymentsToAcquireProductiveAssets=[fact(*FY25, 15)],
        ),
        URL,
    )
    assert result.series["capex"][0].value == 10


def test_a_calculated_key_figure_is_never_taken_from_an_old_year() -> None:
    """Found on live data: FCF from FY2012 was shown beside FY2026 figures."""
    result = overview(
        doc(
            Revenues=[fact(*FY24, 100), fact(*FY25, 110)],
            NetIncomeLoss=[fact(*FY24, 10), fact(*FY25, 11)],
            NetCashProvidedByUsedInOperatingActivities=[fact(*FY24, 40)],
            PaymentsToAcquirePropertyPlantAndEquipment=[fact(*FY24, 15)],
        ),
        URL,
    )
    figures = {f.metric_id: f for f in result.key_figures}
    assert figures["fcf"].fiscal_year_label == "FY2025"
    assert (figures["fcf"].status, figures["fcf"].value) == ("unavailable", None)
    assert figures["operating_cash_flow"].fiscal_year_label == "FY2025"
    assert figures["operating_cash_flow"].status == "missing"
    assert figures["net_margin"].fiscal_year_label == "FY2025"
''')
    sub("backend/tests/test_periods_m2.py", [
        ('''from app.logic.statements import build_financials
''', '''from app.logic.statements import build_financials, overview
'''),
    ])
else:
    sub("backend/app/logic/metrics.py", [
        ('''NO_DEBT_CONCEPT = "no debt concept reported"
''', '''NO_DEBT_CONCEPT = "no debt concept reported"
NO_LONG_TERM_DEBT = "no long-term debt concept reported"
LONG_TERM_DEBT_IDS = {"debt_long_term_noncurrent", "debt_long_term_current"}
'''),
        ('''    if not reported:
        return _unavailable("debt", base, base.unit, components, NO_DEBT_CONCEPT)
''', '''    if not reported:
        return _unavailable("debt", base, base.unit, components, NO_DEBT_CONCEPT)
    # A short-term line alone says nothing about long-term debt, so a total would understate it,
    # possibly as zero. (Seen on live data: NVIDIA FY2019.)
    if not any(c.metric_id in LONG_TERM_DEBT_IDS for c in reported):
        return _unavailable("debt", base, base.unit, components, NO_LONG_TERM_DEBT)
'''),
    ])
    sub("backend/app/logic/concepts.py", [
        ('''ALL_CONCEPTS = CAPTURE_CONCEPTS
''', '''# PaymentsToAcquireProductiveAssets is outside CAPTURE_CONCEPTS, so it never appears in the recorded
# fixtures. Checked on live data 2026-11-04: NVIDIA tags its capex this way. It can include intangible
# assets, which is why it comes second; the concept used is always shown.
CAPEX_CONCEPTS: tuple[str, ...] = (
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "PaymentsToAcquireProductiveAssets",
)
ALL_CONCEPTS: tuple[str, ...] = (*CAPTURE_CONCEPTS, "PaymentsToAcquireProductiveAssets")
'''),
    ])
    s = open("backend/app/logic/concepts.py").read()
    import re
    s2, n = re.subn(r'_one\(\s*"capex",\s*"Capital expenditure \(capex\)",\s*"PaymentsToAcquirePropertyPlantAndEquipment"\s*\),',
                    'ReportedMetric(\n        "capex", "Capital expenditure (capex)", CAPEX_CONCEPTS, "no mapped capex concept"\n    ),', s)
    assert n == 1
    open("backend/app/logic/concepts.py", "w").write(s2)
    sub("backend/app/logic/statements.py", [
        ('''KEY_FIGURES = (
''', '''# The latest usable value, so a company that stopped reporting one still shows its last figure, dated.
LATEST_USABLE_FIGURES = ("revenue", "net_income")
KEY_FIGURES = (
'''),
        ('''    figures = [_latest_reported(result.series[metric_id]) for metric_id in KEY_FIGURES]
''', '''    # Everything else belongs to the latest period, or says why not: an old value next to the latest
    # figures would look current.
    figures = [
        _latest_reported(result.series[metric_id])
        if metric_id in LATEST_USABLE_FIGURES
        else result.series[metric_id][-1]
        for metric_id in KEY_FIGURES
    ]
'''),
        ('''    key figures always use the latest usable value.
''', '''    key figures use the latest period (revenue and net income: the latest usable value).
'''),
    ])
    fe = "frontend/"
    sub(fe + "components/KeyFigures.tsx", [
        ('''{metric.status === "ok" ? <span className="text-table font-normal text-muted">{unitCaption(metric.unit)}</span> : null}''',
         '''{metric.status === "ok" && metric.unit !== "percent" && metric.unit !== "ratio" ? <span className="text-table font-normal text-muted">{unitCaption(metric.unit)}</span> : null}'''),
    ])
    sub(fe + "components/MetricChart.tsx", [
        ('''        {statusText(metric)} {metric.status === "ok" ? unitCaption(metric.unit) : ""}
''', '''        {statusText(metric)} {metric.status === "ok" && metric.unit !== "percent" && metric.unit !== "ratio" ? unitCaption(metric.unit) : ""}
'''),
    ])
    sub(fe + "components/ValueCell.tsx", [
        ('''className="text-label whitespace-normal text-right text-muted"''',
         '''className="inline-block max-w-[7.5rem] whitespace-normal text-right text-label leading-tight text-muted [overflow-wrap:anywhere]"'''),
    ])
    sub(fe + "components/StatementTable.tsx", [
        ('''import { KindBadge } from "@/components/SourceBadge";
''', '''"use client";

import { useEffect, useRef } from "react";

import { KindBadge } from "@/components/SourceBadge";
'''),
        (''' * from the backend with its status; this table only arranges and formats them.
 */''', ''' * from the backend with its status; this table only arranges and formats them. When the table is wider than its
 * box it opens scrolled to the newest year.
 */'''),
        ('''readonly PeriodInfo[] }) {
  return (
    <div className="table-scroll">
''', '''readonly PeriodInfo[] }) {
  const box = useRef<HTMLDivElement>(null);
  const columns = periods.length;
  useEffect(() => {
    if (box.current) box.current.scrollLeft = box.current.scrollWidth;
  }, [columns]);

  return (
    <div ref={box} className="table-scroll">
'''),
        ('''className="num normal-case">''', '''className="num normal-case whitespace-normal! min-w-[5.5rem] leading-tight py-1!">'''),
    ])
    print("code applied")
print("ok")
