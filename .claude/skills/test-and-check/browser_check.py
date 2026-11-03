"""Browser check template: copy to app/checks/browser_check.py and adapt the CONFIG section.

What it does, against an app that is already running locally:
- opens each page of the main journey in a real (headless) Chromium browser at a laptop and a phone width;
- saves a full-page screenshot of each into app/.browser-checks/ (git-ignored);
- runs the journey's critical interactions (you write them in critical_interactions below);
- fails on: HTTP errors, JavaScript errors in the console, requests to non-local hosts (when the app must
  work offline), content wider than the phone screen, and keyboard focus that never reaches a control.

What it does NOT do: judge whether the page looks right. Someone must look at the screenshots
(see browser-checks.md: "test", "browser check" and "visual inspection" are different things).

Setup (once, inside the app's own virtual environment; never in a base or system Python):
    .venv/bin/python -m pip install -r requirements-dev.txt     # contains: playwright
    .venv/bin/python -m playwright install chromium             # downloads the browser (about 150 MB)
Run (from app/, in a second terminal while the app runs):
    .venv/bin/python checks/browser_check.py http://127.0.0.1:8000
Windows: use .venv\\Scripts\\python instead of .venv/bin/python.
"""

import pathlib
import sys
from urllib.parse import urlparse

from playwright.sync_api import Page, sync_playwright

# ---- CONFIG: adapt to docs/acceptance.md -------------------------------------------------------------------
BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"
PAGES = [  # (name used in the screenshot file, path[, expected HTTP status for error-state pages, e.g. 404])
    ("home", "/"),
]
READY_SELECTOR = "body"  # an element that exists once the page has drawn, e.g. "main", "canvas", "[data-testid='stApp']"
SETTLE_MS = 500  # wait after the page is ready before the screenshot; raise it (e.g. 1500) for Streamlit or slow charts
LOCAL_ONLY = True  # True when every file (scripts, styles, fonts, data) must come from this app, not the internet
WIDTHS = {"laptop": (1366, 800), "phone": (390, 844)}
OUT = pathlib.Path(__file__).resolve().parent.parent / ".browser-checks"


def sign_in(page: Page) -> None:
    """Only if pages need an account: sign in a TEST user that exists in a test or temporary database.
    Read its name and password from environment variables set in the terminal; never hard-code real ones."""


def critical_interactions(page: Page, problems: list[str]) -> None:
    """The journey's key actions, each followed by a check of what the user should see. Example:
        page.get_by_label("Company").select_option("Example Corp")
        page.get_by_role("button", name="Show").click()
        if not page.get_by_text("Revenue").first.is_visible():
            problems.append("after choosing a company, the Revenue card is not visible")
    To capture a chart tooltip, hover a point that has a value (not a gap), then take a page screenshot:
        chart = page.locator("#chart-margin"); chart.scroll_into_view_if_needed()
        box = chart.bounding_box(); chart.hover(position={"x": box["width"] * 0.25, "y": box["height"] * 0.6})
        page.wait_for_timeout(600); page.screenshot(path=OUT / "chart-tooltip-laptop.png")
    """


# ---- The checks (normally no need to edit below) -------------------------------------------------------------
def full_screenshot(page: Page, path: pathlib.Path) -> None:
    """Screenshot of the whole content. Some apps (e.g. Streamlit) scroll inside their own container, so a normal
    full-page screenshot shows only the first screen: make the window as tall as the content first."""
    size = page.viewport_size
    tallest = page.evaluate(
        "Math.max(document.documentElement.scrollHeight, ...Array.from(document.querySelectorAll('*'))"
        ".filter(e => e.scrollHeight > e.clientHeight + 1).map(e => e.scrollHeight))"
    )
    page.set_viewport_size({"width": size["width"], "height": min(max(tallest, size["height"]), 12_000)})
    try:
        page.wait_for_timeout(500)
        page.screenshot(path=path, full_page=True)
    finally:
        page.set_viewport_size(size)


def check_page(page: Page, name: str, path: str, width: str, problems: list[str], expected: int = 200) -> None:
    response = page.goto(BASE_URL + path, wait_until="load")
    status = response.status if response else None
    if status != expected and not (expected == 200 and status is not None and status < 400):
        problems.append(f"{name} ({width}): HTTP {status or 'no response'}, expected {expected}")
        return
    page.wait_for_selector(READY_SELECTOR, timeout=10_000)
    page.wait_for_timeout(SETTLE_MS)  # let the page and charts finish drawing before the screenshot
    full_screenshot(page, OUT / f"{name}-{width}.png")
    too_wide = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
    if width == "phone" and too_wide:
        problems.append(f"{name} (phone): content is wider than the screen (sideways scrolling)")
    page.keyboard.press("Tab")
    focused = page.evaluate("document.activeElement ? document.activeElement.tagName : 'BODY'")
    if focused in ("BODY", "HTML"):
        problems.append(f"{name} ({width}): the Tab key does not reach any control")


def main() -> int:
    OUT.mkdir(exist_ok=True)
    problems: list[str] = []
    base_host = urlparse(BASE_URL).hostname
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width, (w, h) in WIDTHS.items():
            page = browser.new_page(viewport={"width": w, "height": h})
            # The browser also logs "Failed to load resource" for every HTTP error, including an expected 404 page;
            # failed files (scripts, styles, images, data) are caught by on_response instead, with their address.
            page.on("console", lambda m, wd=width: m.type == "error" and not m.text.startswith("Failed to load resource")
                    and problems.append(f"console error ({wd}): {m.text}"))
            page.on("response", lambda r, wd=width: r.status >= 400 and r.request.resource_type != "document"
                    and problems.append(f"file failed to load ({wd}): HTTP {r.status} {r.url}"))
            page.on("pageerror", lambda e, wd=width: problems.append(f"JavaScript error ({wd}): {e}"))

            def on_request(req, wd=width):
                host = urlparse(req.url).hostname
                if LOCAL_ONLY and host not in (base_host, "localhost", "127.0.0.1", None):
                    problems.append(f"non-local request ({wd}): {req.url}")

            page.on("request", on_request)
            try:
                sign_in(page)
                for name, path, *expected in PAGES:
                    check_page(page, name, path, width, problems, *expected)
                if width == "laptop":
                    critical_interactions(page, problems)
                    full_screenshot(page, OUT / "after-interactions-laptop.png")
            except Exception as error:  # a step that cannot run is a finding, not a crash
                problems.append(f"check stopped ({width}): {type(error).__name__}: {str(error).splitlines()[0]}")
                page.screenshot(path=OUT / f"stopped-{width}.png", full_page=True)
            page.close()
        browser.close()
    print(f"Screenshots: {OUT}")
    for problem in problems:
        print(f"PROBLEM: {problem}")
    print("Browser check:", "FAILED" if problems else "no problems found (now look at the screenshots)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
