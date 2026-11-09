# Classroom guide

**Repository:** <https://github.com/jfimbett/app-creator>

**`main` contains M4 functionality** (tag `m4`), as of 2026-11-09. M3 and M4 were verified on Windows 11.
The old branch `wip/m3-filing-intelligence-unverified` is kept only as history; use `m3` instead.

## Versions

| Version | What it adds | Branch | Tag | Status |
|---|---|---|---|---|
| Template | the toolkit, with no app yet | `template` | `template-v1` | verified |
| M1 Foundation | dark shell, keyboard search, profile, annual revenue and net income from recorded SEC data | `milestone/01-foundation` | `m1` | verified |
| M2 Financial intelligence | Demo/Live choice, statement summaries, ratios, metric explorer, source details | `milestone/02-financial-intelligence` | `m2` | verified |
| M3 Filing intelligence | Filings tab: latest 10-K/10-Q, 10-year history with amendments, a reader with sections, search and sec.gov links | `milestone/03-filing-intelligence` | `m3` | verified (Windows 11) |
| M4 Comparative analysis | Compare screen: 2–4 companies by their own fiscal years, indexing, charts, CSV export | `milestone/04-comparative-analysis` | `m4` | verified (Windows 11) |
| M5 | AI analyst | none | none | not built; only its brief exists |

"Verified" means a checkout passed `npm ci`, `npm run setup` and `npm run verify`: on macOS for M1 and M2, on Windows 11 for M3. Cline and GitHub CI are untested.
Some milestone documents mention an `m5` tag: it does not exist yet.

## What you need installed

- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) 22.13 or newer
- Python 3.10, 3.11, 3.12 or 3.13
- Optional: [Claude Code](https://claude.com/claude-code), for the prompts below

`npm run setup` installs everything else inside the project folder: nothing goes into your system Python or global npm.

## First run: offline demo (start here)

```bash
git clone https://github.com/jfimbett/app-creator.git
cd app-creator
npm ci
npm run setup
npm run demo
```

Open <http://127.0.0.1:3000>. The demo uses recorded SEC data for Apple, Microsoft and Alphabet, so it needs no keys, no contact details and no network. Press **Ctrl+C** in that terminal to stop it.

If it says a port is in use, something else holds it. Choose other ports and open the matching address:

```bash
FRONTEND_PORT=3200 BACKEND_PORT=8200 npm run demo   # http://127.0.0.1:3200
```

## Switching versions without losing your edits

Checking out a **tag** shows the completed version. Run these one step at a time:

```bash
# 1. Stop the app: press Ctrl+C in the terminal running it.

# 2. See whether you have edits.
git status

# 3. Only if git status lists changes: save them on your own branch.
git switch -c my-work
git add -A
git commit -m "My edits"

# 4. Switch to the version you want: m1 or m2.
git switch --detach m1

# 5. Update the packages, because they can differ between versions.
npm ci
npm run setup

# 6. Restart.
npm run demo
```

To get your edits back later, stop the app and run `git switch my-work`, then `npm ci`, `npm run setup` and `npm run demo`. To return to the classroom version, use `git switch main` and the same three commands.
Your git-ignored `.env`, caches and packages stay in the folder when you switch.

### Prompts for Claude Code

Start Claude Code in the `app-creator` folder and say, in your own words:

- **Set up:** "Set up this project using its own commands, then start the offline demo and tell me which address to open."
- **Check before switching:** "Do I have any unsaved edits? Show me what they are. Don't change anything yet."
- **Save and switch:** "Stop the running app. If I have edits, save them in a commit on a new branch called my-work, so nothing is lost. Then switch to tag m1, update the packages with npm ci and npm run setup, and start the demo."
- **Compare:** "In plain language, what changed between tags m1 and m2? Don't change any files."
- **Return:** "Stop the app, go back to my branch my-work, update the packages and start the demo."
- **Port problem:** "The port is in use. Don't stop the other program. Start the demo on ports 3200 and 8200 instead."

Check what Claude proposes before you approve it, particularly any command that discards changes, such as `git reset --hard`, `git clean` or `git checkout .`.

## Inspect or rebuild?

- **Inspect a milestone: use its own tag.** `git switch --detach m2` gives you the finished M2. Read and run it. Don't give M2's own `PROMPT.md` to an assistant there, because that work is already done.
- **Rebuild a milestone: start from the previous tag.** You begin before the work exists:

```bash
git switch -c exercise/build-m2 m1
npm ci
npm run setup
```

Then give the assistant [`milestones/02-financial-intelligence/PROMPT.md`](milestones/02-financial-intelligence/PROMPT.md). To build M3 yourself, start from `m2` with [the M3 brief](milestones/03-filing-intelligence/PROMPT.md); to build M4, start from `m3`; to build M5, start from `m4`.
Your result will differ from the tag: replaying a prompt does not reproduce the same code. The tag is the reference.

The briefs are **not** all the instructions that were actually used. See [the prompt index](milestones/PROMPT-INDEX.md).

## Live mode (separate from the demo, and optional)

Live mode fetches current data from SEC for any US filer. SEC asks automated clients to identify themselves, so **each person uses their own contact**:

1. Create a file named `.env` in the repository root yourself, with this one line:

   ```text
   SEC_USER_AGENT=<a descriptive name> <your own contact email>
   ```

   It is git-ignored, so it stays on your computer. Never commit it, share it or paste it into a chat. Assistants in this project are told not to read or write it.

2. Run `npm run dev`, open <http://127.0.0.1:3000> and change the **Data source** selector in the header from Demo to Live.

Your browser talks only to your own machine; the app's backend talks to SEC, at most one request per second. SEC's fair-access limit of 10 requests per second applies to everyone sharing an address, so **a whole classroom on one network should use the demo**. A live failure shows an error and a button to choose demo data. It never swaps in demo data by itself.

Without the `.env` line, Live says "Live SEC data is not configured" and Demo still works.

## Short demonstrations

### M1 (`git switch --detach m1`)

Press `/`, type `aapl` and choose Apple. Point out the profile with its SEC identifiers, the annual revenue and net income chart, and the `RECORDED SEC DEMO · snapshot <date>` label. Hover over a figure to see its source.

**Limitations.** Three recorded companies only, annual figures only, and no live mode.

### M2 (`git switch --detach m2`)

Open Apple and scroll through the income statement, balance sheet and cash-flow summaries. Change "Years shown". Hover over a ratio to see its formula and inputs. Use the metric explorer to chart a metric. Under `npm run dev` with a contact set, switch to Live and search `NVDA`.

**Limitations.** Summaries are not the complete filed statements. Some concepts are unmapped and show as missing, such as Microsoft's and Alphabet's D&A. Foreign 20-F filers have no statements. Values may reflect later restatements, so they are not point-in-time.

### M3 (`git switch --detach m3`)

Open Apple and choose the **Filings** tab. Point out `Latest in snapshot (as of 2026-11-03)`: in the demo, "latest" always names the snapshot. Click **Read** on the 10-K, click **Item 7** in the section list, then type `revenue` in the search box and step through the matches with the arrows. Click **Source** to open the same document on sec.gov. Then open Alphabet → Filings and find the 2019 `10-K/A`, labelled as an amendment. Untick "Include amendments" to hide it. Under `npm run dev` with a contact set, switch to Live and open NVIDIA's latest 10-K.

**Limitations.** Sections are detected automatically from Item headings and may be imperfect. When none are found, the reader says so and shows the full text. Only the primary document is shown, not the exhibits. The demo has the documents of the latest 10-K and 10-Q of the three companies; other filings open on sec.gov.

### M4 (`main`, or `git switch --detach m4`)

Click **Compare** in the header. Add `aapl`, `msft` and `googl` in the box. Point out the line "AAPL: FY ends 09-26 · MSFT: FY ends 06-30 · GOOGL: FY ends 12-31" and the warning "Fiscal years are not aligned": every value shows its own period end under it. Tick **Index = 100 at first common fiscal year**: revenue becomes `INDEXED` from FY2017 (Apple 208.9 and Microsoft 343.6 in FY2026), while net margin says "not indexed: ratio". Switch the chart between **Trend** and **One year**. Click **Export CSV** and open the file: one line per value, with its SEC concept and accession. Copy the URL into a new tab: the same comparison appears. Under `npm run dev` with a contact set, switch to Live and add NVIDIA as a fourth company.

**Limitations.** No calendar alignment and no currency conversion, by design. One index base year is used for all selected amounts, so adding FCF can move it later. The demo has three companies, so the four-company limit needs Live mode.

## Prompts and records

- **[Milestone and prompt index](milestones/PROMPT-INDEX.md)**: for each milestone, its brief, follow-ups, the prompts actually used, the available responses and the known gaps.
- [All recorded steps](runs/INDEX.md)
- [Planning documents](milestones/README.md)
- [Setup details and troubleshooting](docs/SETUP.md)
