#!/usr/bin/env python3
"""Keep the M1 overview's error code; update M1 tests for M2's intended changes. Run from the backend."""


def sub(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        assert old in s, (path, old[:60])
        s = s.replace(old, new, 1)
    open(path, "w").write(s)


sub("app/errors.py", [
    ('''def _validation_code(exc: RequestValidationError) -> tuple[str, list[str]]:
    """Pick the error code from the first failing parameter; list the parameter names."""
    params = [str(err["loc"][-1]) for err in exc.errors() if err.get("loc")]
    code = next((_CODE_BY_PARAM[p] for p in params if p in _CODE_BY_PARAM), "invalid_request")
    return code, params
''', '''def _validation_code(exc: RequestValidationError, path: str) -> tuple[str, list[str]]:
    """Pick the error code from the first failing parameter; list the parameter names.

    The M1 overview accepts a wider `years` range and keeps its `invalid_request` code.
    """
    params = [str(err["loc"][-1]) for err in exc.errors() if err.get("loc")]
    usable = [p for p in params if not (p == "years" and path.endswith("/overview"))]
    code = next((_CODE_BY_PARAM[p] for p in usable if p in _CODE_BY_PARAM), "invalid_request")
    return code, params
'''),
    ('''async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    code, params = _validation_code(exc)
''', '''async def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    code, params = _validation_code(exc, request.url.path)
'''),
])
sub("tests/test_api_m1.py", [
    ('''    assert set(figures) == {"revenue", "net_income"}
''', '''    assert {"revenue", "net_income"} <= set(figures)  # M2 adds derived figures to the strip
'''),
    ('''    for figure in figures.values():
        assert (figure["unit"], figure["kind"], figure["status"]) == ("USD", "reported", "ok")
''', '''    for figure in (figures["revenue"], figures["net_income"]):
        assert (figure["unit"], figure["kind"], figure["status"]) == ("USD", "reported", "ok")
'''),
    ('''@pytest.mark.parametrize("mode", ["live", "cached", "FIXTURES "])
''', '''@pytest.mark.parametrize("mode", ["cached", "FIXTURES "])  # "live" became valid at M2
'''),
])
print("ok")
