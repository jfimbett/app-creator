# Synthetic test data

SYNTHETIC: invented for tests, not SEC data.

Every file in this folder is made up by hand for automated tests (edge cases such as duplicate facts, 53-week
years or a missing revenue concept). None of it comes from the SEC, and none of it may be shown as SEC data.

- Each JSON file carries a `"_synthetic"` key with the text `SYNTHETIC: invented for tests, not SEC data`; any
  other file states the same in a comment.
- A synthetic fixtures tree for API tests has a `manifest.json` with `"synthetic": true`; the backend then labels
  it `SYNTHETIC TEST DATA`, never `RECORDED SEC DEMO`.
- The running app never reads this folder. Authentic recorded data lives only in `examples/sec-analytics/fixtures/`
  and is written only by `scripts/capture_fixtures.py`.
- `tests/test_fixtures_manifest.py` fails if a file here lacks the marker, or if the marker appears under
  `fixtures/`.
