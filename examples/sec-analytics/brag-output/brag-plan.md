# SEC Analytics — launch video plan (/brag-slim, tone: polished, landscape 1920×1080, 30 fps)

Made on 2026-11-09 for M6 (owner decision O6, brief §9.1) with the installed `/brag` skill, which hands off to
/brag-slim on Opus 5.5. Built only with tools already on the machine: Playwright's Chromium (capture and frame
rendering), Node (a small synthesizer for the music), ffmpeg (encode). Nothing was installed or downloaded.

## What it is

- **One sentence:** a teaching app that turns public SEC EDGAR filings into clear figures, charts, the filings
  themselves and comparisons, with every number linked to the filing it came from.
- **For:** finance and accounting students and their teachers.
- **Sets it apart:** provenance on every value (concept, period, form, accession), missing means missing, a demo
  mode that works offline.
- **Strongest true claim:** hover any figure and see the exact 10-K it came from.
- **Visual hook:** Apple's revenue, 478,834, and its source tooltip opening on top of it.
- **Real UI shown:** Overview with the source tooltip, the landing hero, the revenue/net income chart, the filing
  reader with a search hit, Compare with three companies, the Analyst panel in its "AI not configured" state.
- **Share caption:** see `share-copy.txt`.

## Angle

"Every number, with its filing." Calm and exact, like the app: long holds, soft dips through the navy background,
amber accent. No claims beyond what the app does at m5.

## Honesty rules for this video (brief §6, §9.1)

- Only recorded demo data (snapshot 2026-11-03) for Apple, Microsoft and Alphabet, captured from the running demo
  in fixture mode. No key, no personal data, no real people.
- The fictional testimonials and the illustrative pricing are **not shown**.
- The Analyst appears only in its real "AI not configured" state; no answer is shown or invented.
- The end card says the app is not affiliated with the SEC.

## Music

96 BPM (one beat = 0.625 s), D major, 36 beats = 22.5 s. Chords every 8 beats: Dmaj9 → Bm7 → Gmaj7 → A6sus → D
(resolves under the end card). Soft pad from the first frame; a gentle pluck arpeggio from the reveal; a quiet kick
and hats from the first highlight; a soft swell into each cut and a bell in D on the reveal and the end card. Every
part sits on one beat grid counted from frame 0; every cut lands on a beat.

## Storyboard (cuts on beats)

| # | Beats | Time (s) | Scene | On-screen text (held ≥ 0.3 s/word) | Motion |
|---|---|---|---|---|---|
| 1 | 0–6 | 0.00–3.75 | **Hook.** Apple overview (dark), tight on the revenue card "478,834". At beat 3 the real source tooltip opens on it (cut between two captures of the same layout). | "Where does this number come from?" (0.25–1.85) → "Its SEC filing. One hover away." (2.05–3.6) | slow push-in 1.35→1.45 on the card; tooltip fades in 0.2 s |
| 2 | 6–12 | 3.75–7.50 | **Reveal.** Landing hero (dark): the product's own headline "Understand public companies from their SEC filings" and the app below it. | lower third: "SEC Analytics" | zoom out 1.12→1.0; bell |
| 3 | 12–17 | 7.50–10.63 | **Highlight 1.** Apple revenue and net income chart (light theme). | "Ten years of figures, each with its source." | slow pan right |
| 4 | 17–22 | 10.63–13.75 | **Highlight 2.** Filing reader (dark) with the search "services revenue" and the hit highlighted in Apple's 10-K. | "Read the 10-K itself. Search inside it." | push-in toward the hit |
| 5 | 22–26 | 13.75–16.25 | **Highlight 3.** Compare (light): AAPL, MSFT, GOOGL revenue on their own fiscal years. | "Compare up to four companies." | pan up from table to chart |
| 6 | 26–30 | 16.25–18.75 | **Highlight 4.** Compare (dark) with the Analyst panel open: "AI not configured: add your own OpenRouter key". | "Ask the analyst, with your own key." | push-in on the panel |
| 7 | 30–36 | 18.75–22.50 | **End card.** Brand mark, "SEC Analytics · Demo mode works offline", repository URL, "Public SEC EDGAR data · Not affiliated with the SEC". | as written | staggered fade-up; bell; music resolves and fades |

Transitions: scenes 1→2, 2→3, 5→6 and 6→7 dip through the background (old out 0.2 s, new in 0.25 s); 3→4 and
4→5 also dip, since the themes change (a crossfade between light and dark busy layouts would look muddy).
